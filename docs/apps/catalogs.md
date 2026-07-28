# App: catalogs

## Propósito

La app `catalogs` administra la información de referencia utilizada durante el procesamiento y normalización de facturas.

Su función principal es proporcionar información adicional que puede ser necesaria para validar, normalizar o completar los datos que finalmente se enviarán al layout de salida.

La app maneja dos tipos principales de información:

1. **Catálogos maestros**, como proveedores, monedas y unidades de medida.
2. **Catálogos específicos de proveedores**, que contienen información adicional utilizada para completar los layouts.

Los catálogos son una pieza fundamental del proceso de extracción, ya que no toda la información necesaria para generar el layout final se encuentra directamente en el invoice.

---

## Tipos de información administrada

### Catálogos maestros

La app administra información general utilizada como referencia por el sistema.

Actualmente se contemplan:

* Proveedores (`Supplier`).
* Monedas (`Currency`).
* Unidades de medida (`Umc`).

Esta información proviene principalmente de un sistema externo denominado **Casa**.

La intención es que estos datos sean sincronizados periódicamente desde una base de datos externa para mantener la información actualizada y consistente con el sistema de origen.

Sin embargo, el sistema también permite registrar información manualmente cuando sea necesario.

### Proveedores

El modelo `Supplier` representa a los proveedores cuyos invoices pueden ser procesados por el sistema.

Un proveedor puede tener múltiples templates asociados, ya que un mismo proveedor puede entregar diferentes tipos de documentos o utilizar diferentes estructuras de archivo.

Conceptualmente:

```text
Supplier
   │
   ├── Template
   ├── Template
   └── Template
```

El proveedor también puede tener uno o varios catálogos específicos asociados.

```text
Supplier
   │
   ├── SupplierCatalog
   ├── SupplierCatalog
   └── SupplierCatalog
```

### Monedas

El modelo `Currency` representa el catálogo de monedas utilizado por el sistema.

La información puede utilizarse para validar o normalizar los valores provenientes del invoice.

Por ejemplo, un invoice puede contener una representación de moneda que no coincide exactamente con el formato esperado por el sistema. En estos casos, la información del catálogo permite realizar la correspondencia y utilizar el valor estandarizado.

El catálogo de monedas no necesariamente aporta información que no exista en el invoice. Su función principal es permitir validar o normalizar la información recibida.

### Unidades de medida (UMC)

El modelo `Umc` representa el catálogo de unidades de medida utilizado por el sistema.

Al igual que las monedas, la información puede utilizarse para validar o normalizar valores obtenidos del invoice.

El valor recibido desde el proveedor puede requerir una correspondencia con el valor registrado en el catálogo para garantizar que el resultado final utilice la representación esperada.

---

# Catálogos específicos de proveedores

Los `SupplierCatalog` representan catálogos de información proporcionados por un proveedor.

A diferencia de los catálogos maestros, estos catálogos se utilizan principalmente para obtener información adicional que **no está presente directamente en el invoice**.

Por ejemplo, un invoice puede proporcionar únicamente un número de parte:

```text
PART = 12345
```

El sistema puede utilizar ese valor para buscar información adicional en el catálogo del proveedor:

```text
PART = 12345
DESCRIPTION = Refacción para motor
FRACTION = 8708.99
```

De esta manera, el catálogo permite completar información que no estaba disponible originalmente en el invoice.

El flujo conceptual es:

```text
Invoice
   │
   │ Contiene
   ▼
Valor de referencia
   │
   │ Ejemplo: PART = 12345
   ▼
SupplierCatalog
   │
   │ Busca por pivot
   ▼
SupplierCatalogRow
   │
   │ Obtiene información adicional
   ▼
Campos del Layout
```

---

## SupplierCatalog

El modelo `SupplierCatalog` representa un catálogo específico perteneciente a un proveedor.

Un proveedor puede tener múltiples catálogos.

Por ejemplo:

```text
Supplier: Suzuki
│
├── Catálogo de partes
├── Catálogo de fracciones
└── Catálogo de descripciones
```

Cada catálogo define un campo pivote mediante `pivot_field_name`.

El campo pivote identifica la columna del archivo Excel que será utilizada como clave de búsqueda.

Por ejemplo:

```text
PART
DESCRIPTION
FRACTION
COUNTRY
```

Si `PART` es el campo pivote:

```text
pivot_field_name = "PART"
```

Entonces el valor obtenido del invoice se utilizará para buscar una fila del catálogo mediante ese campo.

El pivote funciona como el vínculo entre la información extraída del invoice y la información almacenada en el catálogo.

```text
Invoice
   │
   │ Extrae PART = 12345
   ▼
pivot_value = 12345
   │
   ▼
SupplierCatalogRow
   │
   │ supplier_catalog = Catálogo Suzuki
   │ pivot_value = 12345
   ▼
Fila encontrada
```

---

## SupplierCatalogColumn

`SupplierCatalogColumn` representa una columna configurada dentro de un `SupplierCatalog`.

Cada columna contiene un `source_name`, que corresponde al nombre de la columna tal como aparece en el archivo Excel del catálogo del proveedor.

Por ejemplo, un archivo puede tener:

```text
PART | DESCRIPTION | FRACTION | BRAND
```

El sistema puede representar estas columnas mediante:

```text
SupplierCatalogColumn
├── PART
├── DESCRIPTION
├── FRACTION
└── BRAND
```

Las columnas se configuran previamente y se utilizan para validar la estructura del archivo cargado.

Cuando un catálogo es cargado, el sistema verifica que el archivo contenga las columnas esperadas.

---

## SupplierCatalogRow

`SupplierCatalogRow` representa una fila individual de información dentro de un catálogo de proveedor.

Cada fila contiene:

* El catálogo al que pertenece.
* El valor pivote utilizado para realizar búsquedas.
* Los valores de las columnas del catálogo.

Los datos de las columnas se almacenan en el campo `data` como un objeto JSON.

Conceptualmente:

```json
{
  "PART": "12345",
  "DESCRIPTION": "Refacción para motor",
  "FRACTION": "8708.99"
}
```

La relación completa es:

```text
SupplierCatalog
       │
       │ 1:N
       ▼
SupplierCatalogRow
       │
       ├── pivot_value
       │
       └── data
```

El `pivot_value` identifica la fila que debe utilizarse durante una búsqueda.

El modelo también mantiene una restricción de unicidad para evitar que un mismo catálogo contenga dos filas con el mismo valor pivote.

```text
SupplierCatalog A
│
├── pivot_value = 12345  ✓
├── pivot_value = 12346  ✓
└── pivot_value = 12345  ✗ duplicado
```

---

# Mapeo de catálogos hacia layouts

Un catálogo puede reutilizarse con diferentes layouts.

Por esta razón, una columna del catálogo no tiene un único destino fijo. El destino depende del layout que se esté procesando.

La relación se define mediante `SupplierCatalogColumnLayoutField`.

Conceptualmente:

```text
SupplierCatalogColumn
        │
        ▼
SupplierCatalogColumnLayoutField
        │
        ▼
LayoutField
```

Esto permite que una misma columna del catálogo pueda alimentar diferentes campos dependiendo del layout.

Por ejemplo:

```text
Catálogo Suzuki
│
└── DESCRIPTION
       │
       ├── Casa Azul
       │      └── LayoutField: product_description
       │
       └── Casa Rojo
              └── LayoutField: item_description
```

El catálogo puede mantenerse reutilizable, mientras que cada layout define su propio mapeo.

Esto evita duplicar el mismo catálogo cuando diferentes layouts requieren utilizar la misma información.

---

# Uso del campo pivote

El campo pivote es el mecanismo que permite relacionar la información del invoice con una fila específica del catálogo.

El proceso general es:

```text
1. El invoice contiene un valor de referencia.
           │
           ▼
2. El TemplateField extrae ese valor.
           │
           ▼
3. El valor extraído se relaciona con el campo
   pivote configurado en SupplierCatalog.
           │
           ▼
4. Se busca una SupplierCatalogRow.
           │
           ▼
5. Se obtienen los valores almacenados en data.
           │
           ▼
6. SupplierCatalogColumnLayoutField determina
   qué campos del layout deben recibir esos valores.
```

Ejemplo:

```text
Invoice
PART = 12345
     │
     ▼
SupplierCatalog
pivot_field_name = PART
     │
     ▼
SupplierCatalogRow
pivot_value = 12345
     │
     ▼
data
{
    "DESCRIPTION": "Refacción para motor",
    "FRACTION": "8708.99"
}
     │
     ▼
SupplierCatalogColumnLayoutField
     │
     ├── DESCRIPTION → LayoutField A
     └── FRACTION → LayoutField B
     │
     ▼
Layout final
```

---

# Carga de catálogos

Los catálogos específicos de proveedores se cargan mediante archivos Excel.

El catálogo debe estar previamente configurado en el sistema con:

* Proveedor.
* Nombre del catálogo.
* Campo pivote.
* Columnas esperadas.

La configuración del catálogo se administra mediante el **Django Admin**.

El archivo Excel cargado debe contener:

* La columna configurada como pivote.
* Todas las columnas configuradas en `SupplierCatalogColumn`.

Durante la carga, el sistema valida que las columnas esperadas existan en el archivo.

Si falta alguna columna requerida, la carga es rechazada.

---

## Reemplazo de información

La carga de un catálogo funciona como una operación de reemplazo completo.

El proceso es:

```text
Archivo Excel
     │
     ▼
Validación
     │
     ▼
Lectura de registros
     │
     ▼
Eliminación de filas anteriores
     │
     ▼
Inserción de nuevas filas
```

La operación se ejecuta dentro de una transacción atómica.

Esto significa que el catálogo se reemplaza completamente con la información del nuevo archivo.

El sistema no agrega únicamente las filas nuevas sobre las existentes; en su lugar, elimina las filas actuales del catálogo y crea nuevamente los registros a partir del archivo cargado.

---

# Validación de duplicados

Durante la carga de un catálogo, el sistema valida que no existan valores pivote duplicados.

Por ejemplo:

```text
PART
-----
12345
12346
12345  ← duplicado
```

Si existen valores duplicados en la columna pivote, la carga del catálogo es rechazada.

Esto garantiza que una búsqueda por `pivot_value` pueda identificar una única fila del catálogo.

La restricción también se encuentra reforzada a nivel de base de datos mediante una restricción de unicidad sobre:

```text
supplier_catalog
pivot_value
```

---

# Eliminación de duplicados en archivos Excel

La app también proporciona un endpoint independiente para limpiar archivos Excel antes de cargarlos.

Este endpoint:

1. Recibe un archivo Excel.
2. Recibe el `SupplierCatalog` al que pertenece.
3. Obtiene automáticamente el `pivot_field_name` configurado.
4. Elimina filas completamente vacías.
5. Elimina filas cuyo campo pivote esté vacío.
6. Elimina registros duplicados utilizando el campo pivote.
7. Conserva la primera aparición de cada valor pivote.
8. Devuelve un nuevo archivo Excel listo para descargar.

Conceptualmente:

```text
Excel original
      │
      ▼
Eliminar filas vacías
      │
      ▼
Eliminar filas sin pivote
      │
      ▼
Eliminar duplicados por pivote
      │
      ▼
Excel limpio
```

El usuario no necesita indicar manualmente cuál columna utilizar para detectar duplicados. El sistema obtiene esta información desde la configuración del `SupplierCatalog`.

Este proceso es independiente de la carga del catálogo.

---

# Responsabilidades

La app `catalogs` es responsable de:

* Administrar proveedores.
* Administrar monedas.
* Administrar unidades de medida.
* Administrar catálogos específicos de proveedores.
* Definir el campo pivote de cada catálogo.
* Definir las columnas esperadas de cada catálogo.
* Almacenar las filas de los catálogos.
* Validar la estructura de archivos Excel cargados.
* Validar la unicidad de los valores pivote.
* Proporcionar información para completar layouts.
* Proporcionar información para validar y normalizar datos.
* Mapear columnas de catálogos hacia campos de layouts.
* Limpiar archivos Excel eliminando registros duplicados.

---

# Lo que NO hace esta app

La app `catalogs` no es responsable de:

* Definir la estructura de los layouts.
* Definir los campos de los layouts.
* Definir cómo se extraen campos desde XML o XLSX de facturas.
* Definir templates de proveedores.
* Ejecutar directamente el proceso completo de extracción de facturas.
* Generar el archivo final de salida.

Estas responsabilidades corresponden principalmente a las apps:

* `layouts`
* `templates`
* `extraction`

La app `catalogs` proporciona información que puede ser utilizada por el proceso de extracción y transformación.

---

# Dependencias

La app `catalogs` mantiene una relación con `layouts` para poder mapear columnas de catálogos hacia campos específicos del layout.

La relación principal es:

```text
SupplierCatalogColumn
        │
        ▼
SupplierCatalogColumnLayoutField
        │
        ▼
LayoutField
```

Durante el procesamiento de una factura, la información de los catálogos puede ser utilizada por el proceso de extracción para completar o normalizar la información que será enviada al layout.

Por lo tanto, conceptualmente:

```text
catalogs
    │
    │ proporciona información
    ▼
extraction
    │
    │ genera / completa
    ▼
layouts
```

---

# Puntos de extensión

### Sincronización con Casa

Actualmente, información como proveedores, monedas y unidades de medida puede ser administrada manualmente, pero está previsto que estos datos puedan sincronizarse periódicamente desde una base de datos externa del sistema Casa.

La implementación de este mecanismo debe mantener la responsabilidad de sincronización separada de la lógica de procesamiento de facturas.

### Nuevos tipos de catálogos

Si el sistema requiere administrar un nuevo catálogo maestro o de referencia, debe evaluarse si corresponde crear un nuevo modelo o extender la estructura existente.

### Nuevas estrategias de búsqueda

Actualmente los catálogos específicos de proveedores utilizan un campo pivote como clave de búsqueda.

Si en el futuro se requieren búsquedas utilizando múltiples campos o claves compuestas, deberá revisarse el diseño actual de `pivot_field_name` y `pivot_value`.

---

# Flujo completo de uso durante una extracción

La utilización de catálogos durante el procesamiento de una factura puede resumirse de la siguiente manera:

```text
                    Invoice
                       │
                       ▼
                 Extracción
                       │
                       ▼
              Valor de referencia
              Ejemplo: PART = 12345
                       │
                       ▼
                SupplierCatalog
                       │
                Busca por pivot
                       │
                       ▼
              SupplierCatalogRow
                       │
                       ▼
                 data (JSON)
                       │
                       ▼
        SupplierCatalogColumnLayoutField
                       │
                       ▼
                 LayoutField
                       │
                       ▼
              Layout de salida
```

Este mecanismo permite que la información adicional de un proveedor se incorpore automáticamente al resultado final sin necesidad de que dicha información esté presente en el invoice original.
