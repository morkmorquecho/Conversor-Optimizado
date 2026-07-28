# App: templates

## Propósito

La app `templates` define cómo debe procesarse la información de un proveedor específico para convertir los datos de un documento de origen en información compatible con un `Layout`.

Mientras que `layouts` define la estructura del archivo final, `templates` define la configuración necesaria para obtener los datos del documento de origen y asociarlos con los campos correspondientes del layout.

Conceptualmente:

```text
Supplier
    │
    ▼
Template
    │
    ├── TemplateField
    │       │
    │       └── TemplateFieldRule
    │
    └── Layout
            │
            └── LayoutField
```

La relación principal es:

```text
Documento del proveedor
        │
        ▼
     Template
        │
        ▼
   TemplateField
        │
        ├── Extrae del documento
        │
        ├── Normaliza
        │
        ▼
   LayoutField
        │
        ▼
Resultado final
```

Un template permite que un mismo layout pueda ser utilizado por diferentes proveedores cuyos archivos de origen tienen estructuras distintas.

---

# Template

El modelo `Template` representa la configuración de extracción de un proveedor para un layout y un tipo de documento específico.

Un template pertenece a:

* Un `Supplier`.
* Un `Layout`.
* Un tipo de documento.
* Un nombre.

Actualmente se soportan dos tipos de documentos estructurados:

* `xlsx`
* `xml`

El template establece la relación:

```text
Proveedor + Layout + Tipo de documento
```

Por ejemplo:

```text
Supplier: Suzuki
Layout: Casa Rojo
Document Type: XLSX
```

Puede representarse como:

```text
Suzuki
   │
   ▼
Template Suzuki XLSX
   │
   ├── Layout: Casa Rojo
   └── Document Type: XLSX
```

El template no representa un archivo individual.

Representa una configuración reutilizable que puede utilizarse para procesar múltiples archivos del mismo proveedor que mantengan la estructura esperada.

---

# Un template por proveedor, layout y formato

El sistema permite que un proveedor tenga diferentes templates.

Por ejemplo:

```text
Suzuki
   │
   ├── Template XLSX → Casa Rojo
   ├── Template XML  → Casa Rojo
   ├── Template XLSX → Casa Azul
   └── Template XML  → Casa Azul
```

Esto permite que el mismo proveedor pueda entregar documentos en diferentes formatos o que sus documentos deban procesarse para diferentes estructuras de salida.

Actualmente existe una restricción para evitar tener más de un template activo para la misma combinación de:

```text
Supplier
Layout
Document Type
```

Por ejemplo, no pueden existir simultáneamente dos templates activos para:

```text
Suzuki + Casa Rojo + XLSX
```

Esto evita ambigüedades al momento de seleccionar automáticamente el template que debe utilizarse para procesar un documento.

---

# Layout y Template

El `Layout` y el `Template` tienen responsabilidades diferentes.

El `Layout` responde:

> ¿Cuál debe ser la estructura del archivo final?

El `Template` responde:

> ¿Cómo obtenemos los datos necesarios para llenar esa estructura desde el documento de este proveedor?

Por ejemplo:

```text
Archivo XLSX Suzuki
        │
        ▼
Template Suzuki XLSX
        │
        ├── "I/V NO"
        │       │
        │       ▼
        │   "NO.FACTURA"
        │
        ├── "I/V DATE"
        │       │
        │       ▼
        │   "FECHA DE FACTURA"
        │
        └── "FOB AMOUNT"
                │
                ▼
            "MONTO DE FACTURA"
```

El template conoce los nombres de los campos del documento de origen.

El layout conoce los nombres de los campos del documento de destino.

Esta separación permite reutilizar un layout entre diferentes proveedores.

---

# TemplateField

Un `TemplateField` define la relación entre un campo del documento de origen y un campo del layout.

Cada `TemplateField` pertenece a:

* Un `Template`.
* Un `LayoutField`.

Además, define:

* `source_field`: nombre del campo que debe buscarse en el documento de origen.
* `extraction_type`: mecanismo utilizado para localizar el valor.
* `worksheet`: hoja del Excel donde debe buscarse el campo, cuando el documento es XLSX.
* `header_occurrence`: ocurrencia del encabezado cuando el mismo nombre aparece varias veces.

Conceptualmente:

```text
TemplateField
    │
    ├── source_field
    │
    ├── extraction_type
    │
    ├── worksheet
    │
    ├── header_occurrence
    │
    └── layout_field
```

Por ejemplo:

```text
source_field:
"I/V NO"

extraction_type:
"header_name"

worksheet:
"Hoja1"

layout_field:
"NO.FACTURA"
```

Esto significa:

> Buscar el campo `I/V NO` en la hoja `Hoja1` y colocar el valor obtenido en el campo `NO.FACTURA` del layout.

---

# Tipos de extracción

Actualmente existen dos tipos de extracción configurables mediante `TemplateField`.

## Header name

```text
header_name
```

Se utiliza principalmente para documentos XLSX.

El sistema busca una columna utilizando el nombre configurado en `source_field`.

Ejemplo:

```text
Archivo XLSX

| I/V NO | I/V DATE | FOB AMOUNT | CURRENCY |
|--------|----------|------------|----------|
| 12345  | 2026-07-01 | 5000     | USD      |
```

Configuración:

```text
source_field = "I/V NO"
extraction_type = "header_name"
worksheet = "Hoja1"
```

Resultado:

```text
I/V NO
  │
  ▼
12345
  │
  ▼
NO.FACTURA
```

---

## XPath

```text
xpath
```

Se utiliza para documentos XML.

En este caso, `source_field` representa la expresión XPath utilizada para localizar el valor dentro del XML.

Conceptualmente:

```text
XML
 │
 ▼
XPath configurado en source_field
 │
 ▼
Valor encontrado
 │
 ▼
LayoutField
```

Esto permite que la misma estructura de configuración `TemplateField` pueda soportar diferentes mecanismos de extracción según el tipo de documento.

---

# Worksheet

El campo `worksheet` indica la hoja de Excel donde se debe buscar la información.

Este campo aplica principalmente a documentos XLSX.

Por ejemplo:

```text
worksheet = "Hoja1"
```

Una configuración puede ser:

```text
TemplateField

source_field:
"PART NO"

extraction_type:
"header_name"

worksheet:
"Hoja1"

layout_field:
"NUMERO DE PARTE"
```

Esto permite identificar tanto la columna como la hoja donde debe buscarse.

Para documentos XML, este campo no es necesario.

---

# Header occurrence

Los archivos Excel pueden contener encabezados repetidos.

Por ejemplo:

```text
| PART NO | DESCRIPTION | PART NO |
|---------|-------------|---------|
| 123     | Motor       | ABC     |
```

En este caso, `header_occurrence` permite indicar cuál de las columnas debe utilizarse.

Por defecto:

```text
header_occurrence = 1
```

Esto significa que se utilizará la primera aparición del encabezado.

Si se configura:

```text
header_occurrence = 2
```

se utilizará la segunda aparición.

Esto permite manejar archivos Excel que tienen nombres de columnas repetidos sin modificar el documento original.

---

# Mapeo entre origen y destino

El objetivo principal de `TemplateField` es realizar un mapeo:

```text
Campo de origen
      │
      ▼
Extracción
      │
      ▼
Normalización
      │
      ▼
Campo de destino
```

Por ejemplo:

```text
Archivo del proveedor

"I/V NO"
"I/V DATE"
"FOB AMOUNT"
"CURRENCY"
"TERM"
"PART NO"
"QTY"

        │
        │ TemplateField
        ▼

Layout Casa Rojo

"NO.FACTURA"
"FECHA DE FACTURA"
"MONTO DE FACTURA"
"MONEDA"
"INCOTERM"
"NUMERO DE PARTE"
"CANTIDAD DE UMC"
```

La configuración de cada `TemplateField` determina cómo se realiza esta correspondencia.

---

# TemplateFieldRule

Un `TemplateFieldRule` permite asociar reglas de normalización a un `TemplateField`.

Su función es definir qué transformaciones deben aplicarse al valor extraído antes de colocarlo en el layout.

La relación es:

```text
TemplateField
      │
      ├── Rule 1
      │
      ├── Rule 2
      │
      └── Rule 3
```

Las reglas se ejecutan según el campo `sort_order`.

Por ejemplo:

```text
Valor extraído
      │
      ▼
Rule #1
      │
      ▼
Rule #2
      │
      ▼
Rule #3
      │
      ▼
Valor final
      │
      ▼
LayoutField
```

Esto permite encadenar múltiples transformaciones sobre un mismo campo.

Por ejemplo, conceptualmente:

```text
" usd "
   │
   ▼
Trim
   │
   ▼
Uppercase
   │
   ▼
Catalog lookup
   │    
   ▼
"USD"
```

La definición de la lógica específica de cada regla corresponde a `NormalizationRule`.

`TemplateFieldRule` únicamente determina qué reglas deben aplicarse a un campo y en qué orden.

---

# Normalización

Las reglas de normalización permiten adaptar la información extraída del documento al formato esperado por el sistema.

Esto es necesario porque los proveedores pueden utilizar valores diferentes a los valores oficiales utilizados por el sistema.

Por ejemplo:

```text
Documento del proveedor:

"US DOLLAR"

        │
        ▼
NormalizationRule

        │
        ▼

"USD"
```

En otros casos, la información puede requerir una consulta a un catálogo para obtener el valor oficial.

Por ejemplo:

```text
Invoice
   │
   ▼
"United States Dollar"
   │
   ▼
Currency Catalog
   │
   ▼
"USD"
```

La normalización permite que el valor final sea consistente con los catálogos y con los valores esperados por el layout.

---

# Relación con catalogs

Los templates trabajan junto con la app `catalogs`.

La diferencia principal es:

```text
Template
    │
    │ define cómo extraer
    ▼
Información presente en el invoice
```

Mientras que:

```text
Catalog
    │
    │ proporciona información adicional
    │ o normaliza información existente
    ▼
Información final del layout
```

Un dato puede seguir diferentes caminos.

### Dato presente en el invoice

```text
Invoice
   │
   ▼
TemplateField
   │
   ▼
NormalizationRule
   │
   ▼
LayoutField
```

### Dato que requiere un catálogo

```text
Invoice
   │
   ▼
TemplateField
   │
   ▼
Valor pivote
   │
   ▼
SupplierCatalog
   │
   ▼
Información adicional
   │
   ▼
LayoutField
```

Por lo tanto, un template no necesariamente representa todos los datos que terminarán en el layout.

Algunos campos pueden completarse posteriormente mediante catálogos.

---

# Restricción de LayoutField

Cada `TemplateField` debe apuntar a un `LayoutField` perteneciente al mismo layout del template.

Por ejemplo:

```text
Template
   │
   └── Layout: Casa Rojo
           │
           └── TemplateField
                   │
                   └── LayoutField: NO.FACTURA
```

No sería válido configurar:

```text
Template
   │
   └── Layout: Casa Rojo
           │
           └── TemplateField
                   │
                   └── LayoutField de Casa Azul
```

Esta validación evita que un template termine escribiendo información en una estructura de salida diferente a la que tiene configurada.

---

# Template para XLSX

Un template XLSX normalmente define campos mediante el nombre de los encabezados.

Ejemplo:

```text
Template
├── Supplier: Suzuki
├── Layout: Casa Rojo
└── Document Type: XLSX
```

Sus campos pueden ser:

```text
"I/V NO"
    └──► NO.FACTURA

"I/V DATE"
    └──► FECHA DE FACTURA

"FOB AMOUNT"
    └──► MONTO DE FACTURA

"CURRENCY"
    └──► MONEDA

"TERM"
    └──► INCOTERM

"PART NO"
    └──► NUMERO DE PARTE

"QTY"
    └──► CANTIDAD DE UMC
```

El usuario únicamente debe seleccionar el template correspondiente al procesar el archivo.

El sistema utiliza la configuración del template para realizar la extracción y construir el resultado.

---

# Template para XML

Un template XML utiliza el mismo concepto general, pero cambia el mecanismo de extracción.

En lugar de buscar una columna mediante un encabezado, el sistema utiliza una expresión XPath.

Conceptualmente:

```text
Template XML
      │
      ▼
TemplateField
      │
      ├── source_field = XPath
      │
      └── extraction_type = xpath
      │
      ▼
Valor extraído
      │
      ▼
LayoutField
```

Esto permite mantener una configuración uniforme para diferentes formatos de documentos.

---

# Configuración desde Django Admin

La configuración de templates está pensada para administrarse desde el Django Admin.

El flujo general para configurar un nuevo proveedor es:

```text
1. Crear o registrar Supplier
       │
       ▼
2. Seleccionar Layout
       │
       ▼
3. Crear Template
       │
       ├── Proveedor
       ├── Layout
       ├── Nombre
       └── Tipo de documento
       │
       ▼
4. Crear TemplateFields
       │
       ├── Campo de origen
       ├── Tipo de extracción
       ├── Hoja (XLSX)
       ├── Ocurrencia
       └── Campo del Layout
       │
       ▼
5. Configurar reglas de normalización
   cuando sean necesarias
       │
       ▼
6. Procesar documentos utilizando el Template
```

Una vez configurado el template, los usuarios no necesitan definir nuevamente los campos de extracción cada vez que suben una factura.

El template representa la configuración reutilizable para ese proveedor y formato.

---

# PDF y PdfExtractionConfig

Los archivos PDF representan un flujo diferente al utilizado para XLSX y XML.

En XLSX y XML existen campos estructurados que pueden ser configurados mediante `TemplateField`.

En un PDF, especialmente cuando se trata de facturas con formatos variables, puede no existir una estructura de campos confiable que permita realizar una extracción directa mediante encabezados o XPath.

Por este motivo, los PDFs utilizan una configuración independiente mediante `PdfExtractionConfig`.

Conceptualmente:

```text
PDF
 │
 ▼
Extracción de texto
 │
 ▼
LLM
 │
 ├── base_prompt
 ├── hints
 │
 ▼
Información estructurada
 │
 ▼
Layout
```

`PdfExtractionConfig` pertenece a un proveedor y a un layout.

Contiene:

* `supplier`: proveedor al que corresponde la configuración.
* `layout`: estructura de salida que debe generarse.
* `base_prompt`: prompt principal utilizado para instruir al LLM.
* `hints`: instrucciones específicas del proveedor o del documento.
* `is_active`: permite habilitar o deshabilitar una configuración.

La configuración permite adaptar el procesamiento del PDF a las particularidades de cada proveedor.

Por ejemplo, los `hints` pueden indicar:

* Dónde se encuentra la moneda.
* Cómo identificar el número de factura.
* En qué sección aparecen las partidas.
* Cómo interpretar determinados valores.
* Particularidades conocidas del formato del proveedor.

---

# Flujo general de Templates

Para documentos XLSX y XML:

```text
Usuario
   │
   │ selecciona Template
   ▼
Template
   │
   ├── Supplier
   ├── Layout
   └── Document Type
        │
        ▼
   TemplateFields
        │
        ├── Extraer
        │
        ▼
   NormalizationRules
        │
        ├── Normalizar
        │
        ▼
   Catalogs
        │
        ├── Completar / validar / normalizar
        │
        ▼
   LayoutFields
        │
        ▼
   Excel final
```

Para documentos PDF:

```text
Usuario
   │
   │ selecciona configuración PDF
   ▼
PdfExtractionConfig
   │
   ▼
Extraer texto del PDF
   │
   ▼
LLM
   │
   ├── base_prompt
   └── hints
   │
   ▼
Datos estructurados
   │
   ▼
Layout
   │
   ▼
Excel final
```

El procesamiento PDF es, por tanto, un flujo separado del mecanismo principal de templates estructurados, aunque ambos terminan utilizando un `Layout` como estructura de salida.

---

# Responsabilidades

La app `templates` es responsable de:

* Asociar proveedores con layouts.
* Definir el tipo de documento que puede procesarse.
* Definir cómo localizar campos en documentos XLSX.
* Definir cómo localizar campos en documentos XML.
* Asociar campos de origen con campos de destino.
* Definir la hoja de Excel donde buscar información.
* Manejar encabezados repetidos en archivos XLSX.
* Asociar reglas de normalización a campos extraídos.
* Definir la configuración de procesamiento de PDFs mediante LLM.

---

# Lo que NO hace esta app

La app `templates` no es responsable de:

* Definir la estructura del archivo final.
* Crear los campos de un layout.
* Almacenar los datos de los catálogos.
* Eliminar duplicados de catálogos.
* Ejecutar por sí misma la extracción de archivos.
* Leer directamente los archivos durante la configuración.
* Generar físicamente el Excel final.
* Implementar la lógica interna de cada regla de normalización.

Estas responsabilidades pertenecen a otras partes del sistema, principalmente `layouts`, `catalogs` y `extraction`.

---

# Puntos de extensión

La arquitectura permite extender el sistema mediante nuevos tipos de extracción.

Actualmente:

```text
header_name
xpath
```

Si en el futuro se necesita soportar otro mecanismo de extracción, puede agregarse un nuevo `ExtractionType` y su lógica correspondiente en el motor de extracción.

Por ejemplo, podrían incorporarse mecanismos especializados para:

* Posiciones específicas de celdas.
* Expresiones regulares.
* JSON.
* Tablas de Excel con estructuras especiales.

También es posible extender las reglas de normalización mediante nuevos tipos de `NormalizationRule`, sin modificar necesariamente la estructura de `TemplateField`.

Para PDFs, pueden agregarse configuraciones específicas por proveedor y layout mediante `PdfExtractionConfig`.

---

# Decisiones de diseño relevantes

## Separación entre Template y Layout

El layout define la estructura de salida, mientras que el template define cómo obtener la información de un proveedor.

Esto evita acoplar el formato del proveedor con el formato final.

Un mismo layout puede ser utilizado por múltiples proveedores:

```text
Proveedor A ──► Template A ──┐
                              │
Proveedor B ──► Template B ──┼──► Casa Rojo
                              │
Proveedor C ──► Template C ──┘
```

Cada proveedor puede tener nombres y estructuras diferentes en sus documentos, pero todos pueden generar el mismo formato de salida.

---

## Separación entre extracción y normalización

El `TemplateField` determina cómo localizar y extraer un valor.

El `TemplateFieldRule` determina qué reglas de normalización deben aplicarse posteriormente.

Esta separación permite cambiar la forma de normalizar un valor sin cambiar necesariamente la configuración utilizada para encontrarlo en el documento.

---

## Los PDFs utilizan un flujo independiente

Los documentos XLSX y XML cuentan con estructuras que permiten configurar campos mediante `TemplateField`.

Los PDFs pueden requerir interpretación del contenido mediante un LLM.

 Por este motivo, la configuración de PDF se mantiene separada mediante `PdfExtractionConfig`, aunque continúa utilizando un `Layout` como estructura final.
