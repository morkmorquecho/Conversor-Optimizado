# App: layouts

## Propósito

La app `layouts` define las estructuras de salida que utiliza el sistema para generar los archivos Excel finales.

Un `Layout` representa un formato de salida completo y está compuesto por uno o varios `LayoutField`, donde cada `LayoutField` representa una columna del archivo Excel final.

La responsabilidad de esta app es definir **qué estructura debe tener el archivo de salida**, pero no definir de dónde provienen los valores que se colocarán en cada campo.

La obtención de los valores corresponde a otras partes del sistema, principalmente `templates`, `catalogs` y `extraction`.

Conceptualmente:

```text
Layout
   │
   ├── LayoutField
   ├── LayoutField
   ├── LayoutField
   └── ...
```

Por ejemplo, un layout puede definir:

```text
NUMERO DE PARTE
DESCRIPCION
CANTIDAD
UMC
MONEDA
```

El layout establece que estas columnas deben existir en el archivo de salida y en qué orden deben aparecer.

---

# Layout

El modelo `Layout` representa una estructura de salida.

Cada layout tiene:

* Un código único.
* Un nombre.
* Un estado activo.

El código permite identificar el layout de forma estable dentro del sistema.

Actualmente existen dos layouts principales:

* `casa_azul`
* `casa_rojo`

Estos corresponden a los formatos de salida utilizados por el sistema Casa.

Aunque la arquitectura está diseñada para permitir diferentes layouts, estos dos formatos representan actualmente las estructuras principales del sistema.

---

# LayoutField

Un `LayoutField` representa un campo o columna dentro de un layout.

Su función es definir:

* El nombre de la columna.
* El layout al que pertenece.
* El orden en el que debe aparecer dentro del archivo Excel final.

Por ejemplo, el layout `Casa Rojo` contiene campos como:

```text
1. CLAVE DEL PROVEEDOR
2. NO.FACTURA
3. FECHA DE FACTURA
4. MONTO DE FACTURA
5. MONEDA
6. INCOTERM
7. SUBDIVISION
8. CERT. ORIGEN
9. NUMERO DE PARTE
10. PAIS ORIGEN
11. PAIS VENDEDOR
12. FRACCION
13. DESCRIPCION
14. VALOR DE LA MERCANCIA
15. UMC
16. CANTIDAD DE UMC
17. CANTIDAD DE UMT
18. PREFERENCIA ARANCELARIA
19. Marca
20. Modelo
21. Submodelo
22. No. Serie
23. Descripción Cove
```

El campo `sort_order` permite mantener el orden esperado de las columnas al generar el archivo final.

Por lo tanto, el `LayoutField` representa tanto el **destino de la información** como su **posición dentro del resultado final**.

---

# El layout como estructura de destino

El layout debe entenderse como el contrato que define la estructura del archivo final.

Por ejemplo:

```text
                 Layout
                    │
                    ▼
        ┌──────────────────────┐
        │ NUMERO DE FACTURA    │
        │ DESCRIPCION          │
        │ CANTIDAD             │
        │ UMC                  │
        │ MONEDA               │
        └──────────────────────┘
```

El layout no necesita conocer si `NUMERO DE FACTURA` proviene de:

* Un archivo XLSX.
* Un XML.
* Un PDF.
* Un catálogo.
* Una normalización.
* Una combinación de diferentes fuentes.

Su única responsabilidad es definir que ese campo existe y dónde debe aparecer en el resultado.

Esta separación permite que el mismo layout sea utilizado por diferentes proveedores.

---

# Relación con Templates

Los `Layout` y los `Template` tienen responsabilidades diferentes.

El `Layout` define:

> **¿Cómo debe ser el resultado final?**

El `Template` define:

> **¿Cómo obtenemos los datos de un proveedor específico para llenar ese resultado?**

La relación conceptual es:

```text
Supplier
    │
    ▼
Template
    │
    │ utiliza
    ▼
Layout
    │
    ▼
LayoutFields
```

Por ejemplo:

```text
Proveedor Suzuki
       │
       ▼
Template Suzuki XLSX
       │
       ▼
Casa Rojo
       │
       ▼
LayoutFields
```

El template puede indicar:

```text
"I/V NO"  ──────────► "NO.FACTURA"
"I/V DATE" ─────────► "FECHA DE FACTURA"
"FOB AMOUNT" ───────► "MONTO DE FACTURA"
"CURRENCY" ─────────► "MONEDA"
"PART NO" ───────────► "NUMERO DE PARTE"
```

En este caso:

* `I/V NO` pertenece al archivo de origen del proveedor.
* `NO.FACTURA` pertenece al layout de destino.

El layout únicamente conoce `NO.FACTURA`.

La lógica que determina que debe obtenerse desde `I/V NO` pertenece al template.

---

# Relación con Catálogos

Los layouts también pueden recibir información proveniente de catálogos.

En estos casos, una columna de un catálogo puede estar asociada a un `LayoutField`.

La relación se realiza mediante:

```text
SupplierCatalogColumn
        │
        ▼
SupplierCatalogColumnLayoutField
        │
        ▼
LayoutField
```

Esto permite que la información de un catálogo pueda completar campos del layout que no estaban presentes originalmente en el invoice.

Por ejemplo:

```text
Invoice
PART = 12345
    │
    ▼
SupplierCatalog
    │
    ▼
DESCRIPTION = "Refacción para motor"
    │
    ▼
LayoutField
DESCRIPCION
```

El layout no necesita conocer el origen de la información.

Solo define el campo de destino.

---

# Layouts actuales

Actualmente el sistema cuenta con dos layouts principales.

## Casa Azul

Código:

```text
casa_azul
```

Campos actuales:

```text
1. NUMERO DE FACTURA
2. DESCRIPCION
3. CANTIDAD DE LA FACTURA
4. UNIDAD DE LA FACTURA
5. PRECIO DE LA PARTIDA
6. MODELO
7. MARCA
8. SUBMODELO
9. SERIE
```

## Casa Rojo

Código:

```text
casa_rojo
```

Campos actuales:

```text
1. CLAVE DEL PROVEEDOR
2. NO.FACTURA
3. FECHA DE FACTURA
4. MONTO DE FACTURA
5. MONEDA
6. INCOTERM
7. SUBDIVISION
8. CERT. ORIGEN
9. NUMERO DE PARTE
10. PAIS ORIGEN
11. PAIS VENDEDOR
12. FRACCION
13. DESCRIPCION
14. VALOR DE LA MERCANCIA
15. UMC
16. CANTIDAD DE UMC
17. CANTIDAD DE UMT
18. PREFERENCIA ARANCELARIA
19. Marca
20. Modelo
21. Submodelo
22. No. Serie
23. Descripción Cove
```

Estos layouts representan los formatos de salida utilizados actualmente por el sistema.

---

# Definición mediante seeds

Los layouts actuales se crean mediante una migración de datos (`RunPython`) que funciona como seed.

La migración crea:

1. El layout.
2. Los campos del layout.
3. El orden de cada campo.

Por ejemplo:

```text
Migration
    │
    ▼
Layout: casa_rojo
    │
    ├── LayoutField 1
    ├── LayoutField 2
    ├── LayoutField 3
    └── ...
```

La definición inicial de los layouts forma parte del código fuente del proyecto.

Esto se debe a que el sistema actual es una evolución de un sistema legacy en el que los formatos de Casa Azul y Casa Rojo eran estructuras centrales y prácticamente fijas.

La nueva arquitectura desacopla estos formatos de la lógica de extracción y permite que el sistema pueda soportar otros layouts, pero los layouts principales siguen estando definidos como parte del código inicial del sistema.

---

# Agregar un nuevo layout

La arquitectura permite agregar nuevos layouts además de Casa Azul y Casa Rojo.

El proceso general es:

```text
1. Crear Layout
       │
       ▼
2. Definir LayoutFields
       │
       ▼
3. Definir el sort_order
       │
       ▼
4. Crear Templates para los proveedores
       │
       ▼
5. Configurar TemplateFields
       │
       ▼
6. Configurar mappings de catálogos
   cuando sea necesario
```

El layout debe existir antes de crear templates que lo utilicen.

---

# Responsabilidades

La app `layouts` es responsable de:

* Definir las estructuras de salida.
* Administrar los layouts disponibles.
* Definir los campos de cada layout.
* Definir el orden de las columnas de salida.
* Servir como estructura de destino para los datos extraídos.
* Permitir que templates diferentes utilicen una misma estructura de salida.
* Permitir que los catálogos mapeen información hacia campos específicos.

---

# Lo que NO hace esta app

La app `layouts` no es responsable de:

* Extraer información de archivos.
* Leer archivos XML.
* Leer archivos XLSX de proveedores.
* Procesar archivos PDF.
* Determinar de qué campo de origen se obtiene un valor.
* Normalizar valores.
* Consultar catálogos.
* Definir proveedores.
* Definir templates.
* Ejecutar el pipeline de extracción.

La app únicamente define la estructura y los campos de destino.

---

# Dependencias

La app `layouts` es utilizada por otras partes del sistema para definir la estructura final de los datos.

Las principales relaciones conceptuales son:

```text
layouts
   ▲
   │
   │ utiliza
   │
templates
   │
   │ define cómo llenar
   │
   ▼
extraction
```

También existe una relación con `catalogs`:

```text
catalogs
   │
   │ proporciona información
   ▼
SupplierCatalogColumnLayoutField
   │
   ▼
layouts.LayoutField
```

Por lo tanto, `layouts` representa una estructura de destino compartida por el resto del sistema.

---

# Puntos de extensión

La arquitectura está diseñada para permitir la incorporación de nuevos layouts.

Agregar un nuevo layout implica definir:

* Un nuevo código.
* Un nombre.
* Sus `LayoutFields`.
* El orden de sus campos.

Después de crear el layout, pueden configurarse templates específicos de proveedores para utilizarlo.

También pueden configurarse mappings entre columnas de catálogos y los nuevos `LayoutFields` cuando el procesamiento requiera información adicional proveniente de catálogos.

Esto permite que la arquitectura pueda crecer más allá de los formatos actuales de Casa Azul y Casa Rojo sin modificar necesariamente el motor general de extracción.
