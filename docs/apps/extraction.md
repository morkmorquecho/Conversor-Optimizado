# App: extraction

## Propósito

La app `extraction` es responsable de ejecutar el proceso de extracción y transformación de facturas hacia un layout de salida definido.

El sistema recibe una factura en alguno de los formatos soportados y utiliza la configuración correspondiente para obtener la información necesaria, normalizarla, complementar los datos mediante catálogos cuando sea necesario y generar un archivo de salida utilizando la estructura del layout seleccionado.

Actualmente se contemplan tres formatos de entrada:

* `XLSX`
* `XML`
* `PDF`

El flujo principal está orientado a archivos `XLSX` y `XML`, donde la extracción se realiza mediante un `Template` asociado a un proveedor y a un `Layout`. El template define qué información debe extraerse del archivo de origen y a qué campo del layout debe dirigirse.

Los archivos `PDF` representan un flujo diferente. Debido a que la información de una factura PDF no necesariamente tiene una estructura fija o campos identificables directamente, se utiliza extracción de texto mediante `pdfplumber` y posteriormente un LLM para interpretar la información. Este proceso utiliza una configuración específica por proveedor mediante `PdfExtractionConfig`.

El resultado final del proceso es un archivo que respeta la estructura del layout seleccionado. Actualmente los layouts principales son `Casa Azul` y `Casa Rojo`, aunque la arquitectura permite trabajar con otros layouts.

---

## Flujo general

El proceso de extracción puede resumirse de la siguiente manera:

```text
Factura de proveedor
        │
        ▼
Identificar proveedor
        │
        ▼
Seleccionar configuración
        │
        ├── XLSX / XML
        │       │
        │       ▼
        │   Template
        │       │
        │       ▼
        │   Extraer campos
        │       │
        │       ▼
        │   Normalizar valores
        │       │
        │       ▼
        │   Consultar catálogo
        │       │
        │       ▼
        │   Completar campos
        │
        └── PDF
                │
                ▼
        Extraer texto con pdfplumber
                │
                ▼
        Interpretar información mediante LLM
                │
                ▼
        Mapear información al Layout

        │
        ▼
Registrar resultados y errores
        │
        ▼
Generar archivo de salida
```

En el caso de archivos `XLSX`, una sola factura puede contener múltiples registros. Cada registro procesado se representa internamente mediante un `ExtractionJob`.

---

## Modelos principales

### `ExtractionBatch`

Representa una ejecución completa del proceso de extracción sobre un archivo.

Un batch contiene la información general de la operación, incluyendo:

* Proveedor.
* Archivo de origen.
* Formato del archivo.
* Estado general del procesamiento.
* Template utilizado, cuando corresponde.
* Configuración de extracción PDF, cuando corresponde.
* Catálogo utilizado, cuando corresponde.
* Cantidad total de registros.
* Cantidad de registros procesados correctamente.
* Cantidad de registros que requieren revisión.
* Fecha de procesamiento.

Un mismo `ExtractionBatch` puede contener múltiples `ExtractionJob`.

Por ejemplo, si un archivo XLSX contiene 500 registros:

```text
ExtractionBatch
├── ExtractionJob - fila 2
├── ExtractionJob - fila 3
├── ExtractionJob - fila 4
├── ...
└── ExtractionJob - fila 501
```

---

### `ExtractionJob`

Representa el procesamiento individual de un registro dentro de un `ExtractionBatch`.

En el flujo XLSX, normalmente cada fila de datos del archivo de entrada genera un `ExtractionJob`.

Cada job puede terminar en uno de los siguientes estados:

* `pending`: pendiente de procesamiento.
* `processed`: procesado correctamente.
* `review`: requiere revisión.
* `error`: procesamiento con error.

El job es la unidad principal utilizada para registrar los resultados y errores de cada registro procesado.

---

### `ExtractionResult`

Representa el resultado obtenido para un campo específico del layout dentro de un `ExtractionJob`.

Cada resultado contiene:

* `layout_field`: campo del layout al que pertenece el resultado.
* `raw_value`: valor obtenido originalmente.
* `normalized_value`: valor después de aplicar las reglas de normalización.

Esto permite conservar tanto el valor original como el valor final utilizado para generar el archivo de salida.

Ejemplo:

```text
raw_value:        "DLS"
normalized_value: "USD"
```

El resultado pertenece a un `LayoutField`, por lo que todos los datos procesados terminan asociados a la estructura definida por el layout.

---

### `ExtractionError`

Registra errores asociados a un `ExtractionJob`.

Un error puede estar relacionado con:

* Un campo específico.
* Un `LayoutField`.
* Un problema al obtener información desde un catálogo.
* Un valor pivote inexistente.
* Una configuración incompleta.
* Cualquier otra situación que impida completar correctamente un registro.

Los errores no necesariamente detienen todo el procesamiento del archivo. En estos casos, el `ExtractionJob` puede quedar en estado `review`, permitiendo que el resto de los registros continúe procesándose.

---

## Responsabilidades

### Esta app SÍ hace

* Recibir archivos de facturas para procesamiento.
* Ejecutar el proceso de extracción configurado.
* Crear y administrar `ExtractionBatch`.
* Crear un `ExtractionJob` por cada registro procesado.
* Extraer información desde archivos XLSX utilizando un `Template`.
* Aplicar reglas de normalización configuradas para cada campo.
* Consultar catálogos de proveedores para complementar información.
* Resolver campos calculados directamente por el sistema.
* Registrar valores originales y normalizados.
* Registrar errores asociados a registros o campos.
* Mantener el estado del procesamiento.
* Generar el archivo Excel final respetando el orden definido por el `Layout`.

### Esta app NO hace

* No define la estructura de los archivos de salida. Esa responsabilidad pertenece a `layouts`.
* No define qué campos deben extraerse de un proveedor. Esa configuración pertenece a `templates`.
* No administra proveedores, monedas, UMC u otros catálogos de referencia. Esa responsabilidad pertenece a `catalogs`.
* No administra la configuración de los layouts. Los layouts principales se crean mediante seeds/migraciones.
* No elimina duplicados de los catálogos durante la extracción. La limpieza de duplicados de catálogos pertenece al flujo de administración de `catalogs`.
* No administra directamente las reglas de normalización. Las reglas se configuran en `layouts` y se encadenan a campos mediante `templates`.
* No decide manualmente qué template utilizar. El consumidor del endpoint proporciona el `template_id` correspondiente.

---

## Dependencias

### `catalogs`

Se utiliza para obtener información de referencia durante la extracción.

Existen dos escenarios principales:

#### Catálogos de complemento

Contienen información que no necesariamente está presente en la factura.

El proceso utiliza un valor pivote obtenido desde la factura para localizar una fila dentro del catálogo. Una vez encontrada, se recuperan las columnas configuradas para completar campos del layout.

Ejemplo:

```text
Factura
NUMERO DE PARTE = ABC123
        │
        ▼
SupplierCatalog
pivot_value = ABC123
        │
        ▼
Catálogo
FRACCION = 12345678
DESCRIPCION = REFACCION AUTOMOTRIZ
PAIS ORIGEN = JAPÓN
        │
        ▼
Layout final
FRACCION
DESCRIPCION
PAIS ORIGEN
```

#### Catálogos de normalización

Los catálogos como `Currency` y `Umc` pueden utilizarse para validar o normalizar información obtenida directamente de la factura.

En este caso, el dato sí existe en la factura, pero puede encontrarse en un formato diferente al requerido por el layout. El sistema realiza un match contra el catálogo para obtener el valor normalizado.

---

### `layouts`

Define la estructura final del documento generado.

Cada layout contiene una colección ordenada de `LayoutField`.

El orden de los `LayoutField` determina el orden de las columnas en el Excel de salida.

Actualmente los layouts principales son:

* `Casa Azul`
* `Casa Rojo`

Estos layouts son creados mediante seeds incluidos en las migraciones del proyecto.

Aunque la arquitectura permite crear nuevos layouts, los layouts principales no se modifican automáticamente durante la operación normal del sistema. Para modificar su estructura se debe modificar el seed/migración correspondiente y ejecutar nuevamente el proceso de migración de forma controlada.

---

### `templates`

Define cómo interpretar un archivo de un proveedor.

Para archivos `XLSX` y `XML`, el `Template` establece la relación:

```text
Proveedor
    │
    ▼
Template
    │
    ├── Tipo de documento
    │
    ├── Layout destino
    │
    └── TemplateFields
            │
            ├── Campo origen
            ├── Tipo de extracción
            └── Campo destino del Layout
```

En el caso de archivos PDF, se utiliza `PdfExtractionConfig`, que contiene la configuración necesaria para que el proceso pueda interpretar el contenido extraído del documento mediante un LLM.

---

## Flujo de extracción XLSX

El flujo principal de extracción de archivos XLSX es:

### 1. Selección del template

El usuario proporciona el archivo de factura y selecciona el `Template` que corresponde al proveedor y formato del documento.

El template determina el layout de salida.

Opcionalmente se puede seleccionar un `SupplierCatalog`.

---

### 2. Lectura del archivo

El sistema abre el archivo XLSX y utiliza la primera hoja del workbook.

Los encabezados de la primera fila se utilizan para identificar las columnas de origen.

Los campos se localizan utilizando el `source_field` configurado en cada `TemplateField`.

---

### 3. Extracción de valores

Cada `TemplateField` indica:

* Qué campo buscar en el archivo.
* Cómo localizarlo.
* A qué `LayoutField` corresponde.

Por ejemplo:

```text
source_field: "PART NO"
extraction_type: "header_name"
layout_field: "NUMERO DE PARTE"
```

Esto significa:

```text
Excel de entrada
PART NO
   │
   ▼
TemplateField
   │
   ▼
LayoutField
NUMERO DE PARTE
```

El sistema también soporta encabezados repetidos mediante `header_occurrence`.

---

### 4. Normalización

Después de obtener el valor original, se ejecutan las reglas asociadas al `TemplateField`.

Las reglas se ejecutan en el orden definido por `sort_order`.

El resultado se guarda como:

```text
raw_value
normalized_value
```

Esto permite conservar el dato original y registrar por separado el valor que será utilizado en la salida.

---

### 5. Consulta de catálogo

Si se configuró un `SupplierCatalog`, el sistema obtiene el valor pivote a partir de un campo previamente extraído.

Ese valor se utiliza para localizar una fila dentro del catálogo.

El campo pivote funciona únicamente como referencia para encontrar el registro correspondiente.

Una vez localizado el registro, se extraen únicamente las columnas que tienen una relación configurada mediante `SupplierCatalogColumnLayoutField`.

Esto permite que un mismo catálogo pueda reutilizarse para diferentes layouts.

---

### 6. Campos de sistema

Algunos campos del layout pueden ser calculados directamente por el sistema.

Por ejemplo:

```text
CLAVE DEL PROVEEDOR
```

se obtiene directamente del código del proveedor asociado al proceso de extracción.

Estos campos no requieren necesariamente estar presentes en el archivo de origen.

---

### 7. Registro del resultado

Cada valor obtenido se guarda como un `ExtractionResult`.

La información queda organizada de la siguiente forma:

```text
ExtractionBatch
    │
    ├── ExtractionJob
    │      ├── ExtractionResult
    │      ├── ExtractionResult
    │      └── ExtractionError (si aplica)
    │
    ├── ExtractionJob
    │      ├── ExtractionResult
    │      └── ...
    │
    └── ...
```

---

### 8. Generación del archivo final

Una vez procesados los registros, se genera un nuevo archivo XLSX.

Las columnas se crean utilizando los `LayoutField` ordenados por `sort_order`.

Cada `ExtractionJob` genera una fila en el archivo final.

El resultado final contiene únicamente la estructura definida por el layout seleccionado.

---

## Estados del procesamiento

### `ExtractionBatch`

| Estado      | Descripción                                          |
| ----------- | ---------------------------------------------------- |
| `pending`   | El proceso fue creado pero aún no ha finalizado.     |
| `processed` | Todos los registros fueron procesados correctamente. |
| `review`    | Uno o más registros requieren revisión.              |
| `error`     | El procesamiento general terminó con un error.       |

### `ExtractionJob`

| Estado      | Descripción                                            |
| ----------- | ------------------------------------------------------ |
| `pending`   | El registro está pendiente de procesamiento.           |
| `processed` | El registro fue procesado correctamente.               |
| `review`    | El registro presenta problemas que requieren revisión. |
| `error`     | El registro no pudo ser procesado correctamente.       |

---

## Puntos de extensión

### Agregar un nuevo formato de archivo

Para soportar un nuevo formato se debe implementar un flujo de extracción específico que:

1. Reciba el archivo.
2. Interprete su contenido.
3. Obtenga los valores de origen.
4. Los transforme al modelo interno de extracción.
5. Genere `ExtractionResult`.
6. Registre los errores correspondientes.
7. Genere el archivo de salida utilizando el `Layout`.

Actualmente los formatos contemplados son:

* XLSX
* XML
* PDF

El flujo XLSX utiliza `InvoiceXlsxExtractionService`.

---

### Agregar un nuevo tipo de extracción

Los `TemplateField` actualmente contemplan tipos como:

* `header_name`
* `xpath`

Esto permite extender el sistema para soportar diferentes estrategias de extracción sin modificar la estructura del layout.

Por ejemplo:

```text
XLSX
    header_name
        │
        ▼
    buscar columna por encabezado

XML
    xpath
        │
        ▼
    buscar nodo mediante XPath
```

---

### Agregar nuevas reglas de normalización

Las reglas de normalización se definen en `NormalizationRule` y se asocian a los campos mediante `TemplateFieldRule`.

Actualmente el procesamiento contempla reglas como:

* `TRIM`
* `UPPERCASE`
* `REGEX_REPLACE`
* `DATE_FORMAT`
* `VALUE_MAP`

El sistema puede extenderse agregando nuevos tipos de reglas.

---

### Agregar nuevas fuentes de información

El flujo puede extenderse para consultar nuevas fuentes de información además de los catálogos actuales.

La arquitectura actual permite separar:

```text
Información del archivo
        │
        ├── Extracción directa
        │
        ├── Normalización
        │
        ├── Catálogo
        │
        └── Campos calculados por sistema
```

Esto permite que un campo del layout pueda obtenerse de diferentes fuentes sin modificar la estructura del layout.

---

## Decisiones de diseño relevantes

### `ExtractionBatch` y `ExtractionJob` están separados

Se utiliza un modelo de batch para representar el procesamiento completo de un archivo y un job para representar cada registro individual.

Esto permite procesar archivos con múltiples registros y conocer exactamente cuáles fueron procesados correctamente y cuáles requieren revisión.

---

### Los resultados se almacenan por `LayoutField`

Los valores extraídos no se almacenan simplemente como un diccionario final.

Cada resultado está relacionado con un `LayoutField`, lo que permite mantener una relación explícita entre el valor obtenido y la estructura de salida.

Además, permite conservar:

```text
raw_value
normalized_value
```

para cada campo.

---

### El catálogo complementa el layout

Los catálogos de proveedores no representan simplemente una fuente alternativa de extracción.

Su principal objetivo es permitir completar información que no está disponible directamente en la factura.

El proceso utiliza un valor pivote obtenido de la factura para localizar la información correspondiente dentro del catálogo.

---

### El campo pivote funciona como referencia

El `pivot_field_name` de un `SupplierCatalog` identifica la columna del catálogo utilizada como clave de búsqueda.

No representa necesariamente un campo que deba aparecer en el resultado final.

Su función principal es permitir:

```text
Valor extraído de la factura
        │
        ▼
Valor pivote
        │
        ▼
Buscar SupplierCatalogRow
        │
        ▼
Obtener información complementaria
```

---

### Los layouts principales están definidos mediante seeds

Los layouts `Casa Azul` y `Casa Rojo` son parte de la estructura base del sistema y se crean mediante migraciones de datos.

Esto se debe a que ambos layouts provienen del sistema legacy y representan las estructuras principales utilizadas actualmente.

Aunque el sistema fue diseñado para permitir nuevos layouts, los layouts existentes no se modifican dinámicamente durante la operación normal.

Una modificación de su estructura requiere cambiar el seed o migración correspondiente y ejecutar el proceso de migración.

---

### La extracción está desacoplada de la estructura de salida

El sistema separa:

```text
Archivo de proveedor
        │
        ▼
Template
        │
        ▼
Extracción
        │
        ▼
Layout
        │
        ▼
Archivo final
```

Esto permite que diferentes proveedores tengan estructuras de entrada diferentes y aun así puedan terminar generando el mismo layout de salida, siempre que exista un `Template` correctamente configurado para cada proveedor.

Por ejemplo:

```text
Proveedor A XLSX ──┐
                   │
Proveedor B XML ───┼──► Layout Casa Rojo
                   │
Proveedor C XLSX ──┘
```

Cada proveedor puede tener su propia configuración de extracción, mientras que la estructura final permanece estandarizada.
