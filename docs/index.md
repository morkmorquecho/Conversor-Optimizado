# Conversor Optimizado

Sistema interno para automatizar la conversión de facturas de proveedores hacia formatos estructurados y definidos por la organización.

Actualmente, el sistema está orientado principalmente a generar los formatos requeridos por CASA mediante los layouts **Casa Azul** y **Casa Rojo**, aunque su arquitectura está diseñada para permitir la incorporación de nuevos layouts y formatos de salida en el futuro.

## Objetivo

El objetivo principal del sistema es reemplazar el proceso manual utilizado anteriormente para procesar facturas y catálogos.

El sistema legacy dependía de una lógica específica para cada archivo y utilizaba archivos Excel como parte del proceso de transformación. Los layouts se manejaban mediante archivos Excel vacíos que eran rellenados durante cada ejecución y posteriormente almacenados. De igual forma, los catálogos de información eran archivos Excel de gran tamaño que debían editarse y mantenerse manualmente.

Conversor Optimizado busca reemplazar este flujo por un sistema centralizado, configurable y escalable que permita:

* Automatizar la conversión de facturas de proveedores al formato requerido por CASA.
* Reducir la dependencia de archivos Excel utilizados como fuente de configuración y procesamiento.
* Centralizar la extracción de información de las facturas.
* Normalizar y validar los datos obtenidos.
* Enriquecer la información utilizando catálogos almacenados y administrados por el sistema.
* Permitir configurar el procesamiento de diferentes proveedores sin implementar una lógica independiente para cada archivo.
* Facilitar la incorporación de nuevos proveedores, formatos de entrada y layouts en el futuro.

## Formatos de entrada

El sistema contempla actualmente tres tipos de documentos de entrada:

* **XLSX**
* **XML**
* **PDF**

Los archivos XLSX y XML utilizan configuraciones basadas en templates para definir cómo debe interpretarse la información de cada proveedor.

Los archivos PDF siguen un flujo diferente, debido a que su información no necesariamente tiene una estructura fija que permita definir campos de extracción de la misma forma que en un Excel o XML. En estos casos se extrae el texto disponible en el documento y posteriormente se utiliza un modelo de lenguaje para interpretar y estructurar la información mediante configuraciones y prompts específicos del proveedor.

## Formatos de salida

La salida del proceso de extracción se genera actualmente en formato **XLSX**.

La estructura del archivo generado está determinada por un **Layout**, que define las columnas y el orden en que deben aparecer en el archivo final.

Actualmente existen dos layouts principales:

* **Casa Azul**
* **Casa Rojo**

Estos layouts representan estructuras utilizadas por el sistema y se encuentran definidos previamente. El diseño del sistema permite incorporar nuevos layouts en caso de que sea necesario soportar nuevos formatos de salida.

## Flujo general

De forma simplificada, el procesamiento de una factura sigue el siguiente flujo:

```text
Factura
   │
   ▼
Identificación del proveedor
   │
   ▼
Configuración de extracción
   │
   ▼
Extracción de información
   │
   ▼
Normalización y validación
   │
   ▼
Enriquecimiento mediante catálogos
   │
   ▼
Generación del Layout
   │
   ▼
Excel final
```

El flujo exacto depende del formato de entrada.

### XLSX y XML

Para estos formatos, el sistema utiliza un **Template** asociado a un proveedor y a un Layout.

El Template define los campos que deben extraerse del documento de entrada y la forma en que se debe localizar cada valor. La información extraída se relaciona con los campos correspondientes del Layout.

Posteriormente, los valores pueden pasar por procesos de normalización y, cuando es necesario, utilizar información proveniente de catálogos para completar o corregir los datos.

El resultado final es un archivo XLSX con la estructura definida por el Layout seleccionado.

### PDF

El procesamiento de PDF utiliza un flujo independiente.

Primero se obtiene el texto disponible en el documento. Debido a que los documentos PDF pueden presentar estructuras diferentes y no siempre cuentan con campos claramente identificables, la extracción se realiza mediante instrucciones específicas para cada proveedor.

Un modelo de lenguaje interpreta el contenido del documento y obtiene la información necesaria para construir los campos requeridos por el Layout.

## Componentes principales

El sistema está dividido conceptualmente en cuatro áreas principales:

### Catalogs

Administra la información utilizada durante el procesamiento de las facturas.

Incluye información general como:

* Proveedores.
* Monedas.
* Unidades de medida (UMC).
* Catálogos específicos de proveedores.

Los catálogos de proveedores permiten complementar información que no está presente directamente en la factura. Por otro lado, catálogos como monedas y UMC pueden utilizarse para validar o normalizar información obtenida desde el documento de entrada.

### Layouts

Define la estructura del archivo final que será generado.

Cada Layout está compuesto por un conjunto de campos ordenados. Estos campos representan las columnas que tendrá el archivo XLSX de salida.

Los layouts principales actualmente son:

* Casa Azul.
* Casa Rojo.

### Templates

Define cómo debe procesarse un documento de un proveedor específico.

Un Template relaciona:

* Un proveedor.
* Un Layout de destino.
* Un tipo de documento de entrada.

Sus campos permiten indicar qué información debe extraerse del documento y a qué campo del Layout debe asignarse.

Los Templates permiten que el procesamiento sea configurable y reutilizable, evitando implementar una lógica independiente para cada proveedor o archivo.

### Extraction

Es el componente encargado de ejecutar el proceso de extracción.

Se encarga de coordinar el procesamiento del archivo, obtener los valores configurados, aplicar normalizaciones, consultar catálogos cuando sea necesario y generar el archivo final utilizando la estructura definida por el Layout.

También registra el resultado del procesamiento y los errores encontrados durante la extracción.

## Administración y configuración

La configuración del sistema se administra desde el panel administrativo.

El flujo de configuración para un nuevo proveedor consiste, de forma general, en:

1. Registrar el proveedor.
2. Seleccionar el Layout que utilizará.
3. Crear el Template correspondiente al tipo de documento.
4. Configurar los campos que deben extraerse.
5. Definir las reglas de normalización cuando sean necesarias.
6. Configurar los catálogos que serán utilizados durante el procesamiento.
7. Asociar los campos de los catálogos con los campos correspondientes del Layout.

Una vez configurada esta información, el procesamiento de una factura consiste principalmente en seleccionar el Template correspondiente y proporcionar el archivo de entrada.

## Arquitectura orientada a configuración

Una de las principales características del sistema es que la lógica de procesamiento no debe depender directamente de un archivo específico.

En lugar de implementar código independiente para cada proveedor, el sistema busca utilizar configuraciones que describan:

* Qué proveedor está procesando el sistema.
* Qué Layout debe generarse.
* Qué campos deben extraerse.
* De dónde deben obtenerse esos campos.
* Cómo deben normalizarse.
* Qué información debe consultarse en los catálogos.
* Cómo debe incorporarse la información complementaria al resultado final.

Este enfoque permite que el sistema sea más mantenible y escalable que el proceso anterior basado en archivos Excel y lógica específica por documento.
