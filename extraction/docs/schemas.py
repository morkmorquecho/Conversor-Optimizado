from core.docs.response import RESPONSE_401


PROCESS_INVOICE_XLSX_SCHEMA = dict(
    tags=['extraction'],
    summary='Procesar factura desde archivo Excel',
    description=(
        'Extrae datos de un archivo Excel de factura utilizando un template '
        'configurado y opcionalmente un catálogo de proveedor.\n\n'
        '**Flujo del proceso:**\n'
        '1. **Validación del archivo:** Verifica que el template sea de tipo XLSX\n'
        '2. **Lectura de encabezados:** Detecta la primera fila de la primera hoja como encabezados\n'
        '3. **Extracción de datos:** Procesa fila por fila desde la fila 2 en adelante\n'
        '4. **Normalización:** Aplica reglas de normalización configuradas (TRIM, UPPERCASE, REGEX_REPLACE, DATE_FORMAT, VALUE_MAP)\n'
        '5. **Búsqueda en catálogo:** Si se proporciona catalog_id:\n'
        '   - Busca el valor pivote en los datos extraídos\n'
        '   - Localiza la fila correspondiente en el catálogo\n'
        '   - Extrae las columnas configuradas en SupplierCatalogColumnLayoutField\n'
        '6. **Campos de sistema:** Resuelve campos calculados (ej: CLAVE DEL PROVEEDOR)\n'
        '7. **Generación de Excel:** Crea un archivo de salida con los resultados\n\n'
        '**Requisitos del archivo:**\n'
        '- Formato: .xlsx o .xls\n'
        '- Primera hoja contiene los datos\n'
        '- Primera fila contiene los encabezados\n'
        '- Los encabezados deben coincidir con los TemplateField.source_field configurados\n\n'
        '**Gestión de errores:**\n'
        '- Filas vacías: Se omiten automáticamente\n'
        '- Valores no encontrados en catálogo: Marca el job para revisión\n'
        '- Cada job individual puede tener errores sin afectar al resto\n\n'
        '**Salida:**\n'
        '- Archivo Excel con los resultados de la extracción\n'
        '- Una fila por cada fila procesada del archivo original\n'
        '- Incluye todas las columnas del Layout en orden de sort_order'
    ),
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Archivo Excel (.xlsx, .xls) de la factura a procesar'
                },
                'template_id': {
                    'type': 'integer',
                    'example': 42,
                    'description': 'ID del template XLSX a utilizar para la extracción'
                },
                'supplier_catalog_id': {
                    'type': 'integer',
                    'example': 15,
                    'description': 'ID del catálogo del proveedor (opcional) para enriquecimiento de datos'
                }
            },
            'required': ['file', 'template_id']
        }
    },
    responses={
        200: {
            'description': 'Archivo procesado exitosamente - descarga directa',
            'content': {
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': {
                    'schema': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Archivo Excel con los datos extraídos'
                    }
                }
            },
            'headers': {
                'Content-Disposition': {
                    'description': 'Nombre del archivo generado',
                    'schema': {
                        'type': 'string',
                        'example': 'attachment; filename="INV_2024_extraccion.xlsx"'
                    }
                },
                'X-Extraction-Batch-Id': {
                    'description': 'ID del lote de extracción creado para seguimiento',
                    'schema': {
                        'type': 'integer',
                        'example': 123
                    }
                }
            }
        },
        400: {
            'description': 'Error en la solicitud o configuración',
            'content': {
                'application/json': {
                    'examples': {
                        'template_invalido': {
                            'summary': 'Template no es de tipo XLSX',
                            'value': {
                                'detail': 'El template seleccionado no es de tipo XLSX.'
                            }
                        },
                        'template_sin_campos': {
                            'summary': 'Template sin campos configurados',
                            'value': {
                                'detail': 'El template no tiene campos configurados para extracción por encabezado.'
                            }
                        },
                        'archivo_sin_datos': {
                            'summary': 'No se encontraron filas de datos',
                            'value': {
                                'detail': 'No se encontraron filas de datos en el excel para el template seleccionado.'
                            }
                        },
                        'encabezados_duplicados': {
                            'summary': 'Encabezados duplicados en el archivo',
                            'value': {
                                'detail': 'El archivo tiene encabezado(s) duplicado(s) en la primera fila: FOB AMOUNT, PRODUCT CODE. Elimina la columna repetida o contacta al área responsable del layout/template antes de volver a subir el archivo.'
                            }
                        },
                        'campos_faltantes': {
                            'summary': 'Faltan campos requeridos en el archivo',
                            'value': {
                                'detail': 'El archivo no contiene los campos requeridos por el template: [nombre_campo1, nombre_campo2]'
                            }
                        },
                        'error_normalizacion': {
                            'summary': 'Error durante la normalización de datos',
                            'value': {
                                'detail': 'Error en la normalización de datos: formato de fecha inválido'
                            }
                        }
                    }
                }
            }
        },
        
        404: {
            'description': 'Recurso no encontrado',
            'content': {
                'application/json': {
                    'examples': {
                        'template_no_encontrado': {
                            'summary': 'Template no existe o está inactivo',
                            'value': {
                                'detail': 'No se encontró el template con ID 42 o no está activo.'
                            }
                        },
                        'catalogo_no_encontrado': {
                            'summary': 'Catálogo no existe o no pertenece al proveedor',
                            'value': {
                                'detail': 'No se encontró el catálogo con ID 15 para el proveedor del template.'
                            }
                        }
                    }
                }
            }
        },
    }
)



PROCESS_INVOICE_PDF_SCHEMA = dict(
    tags=['extraction'],
    summary='Procesar factura desde archivo PDF',
    description=(
        'Extrae datos de un archivo PDF de factura utilizando un template '
        'configurado y opcionalmente un catálogo de proveedor.\n\n'
        '**Flujo del proceso:**\n'
        '1. **Validación del archivo:** Verifica que el archivo pueda ser leído como PDF con texto extraíble\n'
        '2. **Extracción de texto:** Extrae el texto de cada página del PDF mediante pdfplumber\n'
        '3. **Extracción de tablas:** Si el template utiliza el modo `text_and_tables`, también extrae las tablas detectadas en el PDF\n'
        '4. **Extracción estructurada:** Envía el contenido extraído a Gemini utilizando la configuración y estructura definida por el template\n'
        '5. **Procesamiento de campos:** Obtiene los campos de encabezado y, cuando corresponde, los renglones de partida definidos en el template\n'
        '6. **Búsqueda en catálogo:** Si se proporciona un catálogo de proveedor, se utiliza para el enriquecimiento de los datos durante el procesamiento\n'
        '7. **Generación de Excel:** Genera un archivo Excel con los resultados de la extracción\n\n'
        '**Requisitos del archivo:**\n'
        '- Formato: PDF\n'
        '- El PDF debe contener texto extraíble\n'
        '- Los documentos que requieran OCR no pueden procesarse mediante este endpoint\n'
        '- El template seleccionado debe ser de tipo PDF y estar activo\n\n'
        '**Extracción de partidas:**\n'
        '- Si el template tiene campos con scope `line_item`, Gemini debe encontrar renglones de partida en el documento\n'
        '- Si el template solamente tiene campos de encabezado, se genera un único registro\n\n'
        '**Gestión de errores:**\n'
        '- Un PDF que no pueda ser leído como PDF con texto extraíble genera un error de procesamiento\n'
        '- Un PDF sin texto extraíble genera un error de procesamiento y requiere OCR\n'
        '- Los errores durante la extracción estructurada mediante Gemini generan un error de procesamiento\n'
        '- Los errores de procesamiento se devuelven como respuesta HTTP 400\n\n'
        '**Salida:**\n'
        '- Archivo Excel con los datos extraídos\n'
        '- El nombre del archivo se genera utilizando el código del Layout del template\n'
        '- Incluye el identificador del lote de extracción en el header `X-Extraction-Batch-Id`'
    ),
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Archivo PDF de la factura a procesar'
                },
                'template_id': {
                    'type': 'integer',
                    'example': 42,
                    'description': 'ID del template PDF activo a utilizar para la extracción'
                },
                'supplier_catalog_id': {
                    'type': 'integer',
                    'example': 15,
                    'description': 'ID del catálogo del proveedor (opcional) para el enriquecimiento de datos'
                }
            },
            'required': ['file', 'template_id']
        }
    },
    responses={
        200: {
            'description': 'Archivo procesado exitosamente - descarga directa',
            'content': {
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': {
                    'schema': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Archivo Excel con los datos extraídos del PDF'
                    }
                }
            },
            'headers': {
                'Content-Disposition': {
                    'description': 'Nombre del archivo generado',
                    'schema': {
                        'type': 'string',
                        'example': 'attachment; filename="INV_2024_extraccion.xlsx"'
                    }
                },
                'X-Extraction-Batch-Id': {
                    'description': 'ID del lote de extracción creado para seguimiento',
                    'schema': {
                        'type': 'string',
                        'example': '123'
                    }
                }
            }
        },
        400: {
            'description': 'Error en la solicitud, lectura del PDF o procesamiento de la extracción',
            'content': {
                'application/json': {
                    'examples': {
                        'template_invalido': {
                            'summary': 'Template no es de tipo PDF',
                            'value': {
                                'detail': 'El template seleccionado no es de tipo PDF.'
                            }
                        },
                        'pdf_no_legible': {
                            'summary': 'No se pudo leer el PDF',
                            'value': {
                                'detail': 'No se pudo leer el archivo como un PDF con texto extraíble.'
                            }
                        },
                        'pdf_sin_texto': {
                            'summary': 'PDF sin texto extraíble',
                            'value': {
                                'detail': 'El PDF no contiene texto extraíble; se requiere OCR para procesarlo.'
                            }
                        },
                        'error_gemini': {
                            'summary': 'Error durante la extracción estructurada',
                            'value': {
                                'detail': 'No fue posible obtener la extracción estructurada desde Gemini.'
                            }
                        },
                        'respuesta_gemini_invalida': {
                            'summary': 'Respuesta JSON inválida',
                            'value': {
                                'detail': 'Gemini no devolvió una respuesta JSON válida para el template.'
                            }
                        },
                        'estructura_invalida': {
                            'summary': 'Estructura de extracción inválida',
                            'value': {
                                'detail': 'La respuesta de Gemini no coincide con la estructura esperada del template.'
                            }
                        },
                        'sin_renglones': {
                            'summary': 'No se encontraron renglones de partida',
                            'value': {
                                'detail': 'Gemini no encontró renglones de partida para el template seleccionado.'
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Recurso no encontrado',
            'content': {
                'application/json': {
                    'examples': {
                        'template_no_encontrado': {
                            'summary': 'Template no existe o está inactivo',
                            'value': {
                                'detail': 'No se encontró el template con ID 42 o no está activo.'
                            }
                        },
                        'catalogo_no_encontrado': {
                            'summary': 'Catálogo no existe o no pertenece al proveedor',
                            'value': {
                                'detail': 'No se encontró el catálogo con ID 15 para el proveedor del template.'
                            }
                        }
                    }
                }
            }
        },
    }
)


PROCESS_INVOICE_XML_SCHEMA = dict(
    tags=['extraction'],
    summary='Procesar factura desde archivo XML',
    description=(
        'Extrae datos de un archivo XML de factura utilizando un template '
        'configurado y opcionalmente un catálogo de proveedor.\n\n'
        '**Flujo del proceso:**\n'
        '1. **Validación del archivo:** Verifica que el template seleccionado sea de tipo XML\n'
        '2. **Lectura del XML:** Analiza el documento XML y obtiene su elemento raíz\n'
        '3. **Extracción mediante XPath:** Ejecuta los XPath configurados en los TemplateField activos del template\n'
        '4. **Generación de filas:** Cuando un XPath devuelve múltiples coincidencias, genera una fila por cada coincidencia\n'
        '5. **Alineación de valores:** Los valores únicos del comprobante se replican en cada fila y los valores repetidos se alinean por posición\n'
        '6. **Búsqueda en catálogo:** Si se proporciona un catálogo de proveedor, se utiliza para el enriquecimiento de los datos durante el procesamiento\n'
        '7. **Generación de Excel:** Genera un archivo Excel con los resultados de la extracción\n\n'
        '**Requisitos del archivo:**\n'
        '- Formato: XML\n'
        '- El documento debe ser un XML válido\n'
        '- El template seleccionado debe ser de tipo XML y estar activo\n'
        '- Los campos del template utilizan expresiones XPath para definir los valores a extraer\n\n'
        '**Extracción de múltiples registros:**\n'
        '- Los XPath que devuelven un único valor se consideran valores del comprobante y se replican en cada fila generada\n'
        '- Los XPath que devuelven múltiples valores se alinean por posición para conservar los atributos correspondientes de cada registro\n'
        '- El número de filas generadas corresponde a la mayor cantidad de valores obtenidos por los XPath configurados\n\n'
        '**Gestión de errores:**\n'
        '- Un archivo que no sea un XML válido genera un error de procesamiento\n'
        '- Los errores de procesamiento se devuelven como respuesta HTTP 400\n\n'
        '**Salida:**\n'
        '- Archivo Excel con los datos extraídos del XML\n'
        '- El nombre del archivo se genera utilizando el código del Layout del template\n'
        '- Incluye el identificador del lote de extracción en el header `X-Extraction-Batch-Id`'
    ),
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Archivo XML de la factura (CFDI) a procesar'
                },
                'template_id': {
                    'type': 'integer',
                    'example': 42,
                    'description': 'ID del template XML activo a utilizar para la extracción'
                },
                'supplier_catalog_id': {
                    'type': 'integer',
                    'example': 15,
                    'description': 'ID del catálogo del proveedor (opcional) para el enriquecimiento de datos'
                }
            },
            'required': ['file', 'template_id']
        }
    },
    responses={
        200: {
            'description': 'Archivo procesado exitosamente - descarga directa',
            'content': {
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': {
                    'schema': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Archivo Excel con los datos extraídos del XML'
                    }
                }
            },
            'headers': {
                'Content-Disposition': {
                    'description': 'Nombre del archivo generado',
                    'schema': {
                        'type': 'string',
                        'example': 'attachment; filename="INV_2024_extraccion.xlsx"'
                    }
                },
                'X-Extraction-Batch-Id': {
                    'description': 'ID del lote de extracción creado para seguimiento',
                    'schema': {
                        'type': 'string',
                        'example': '123'
                    }
                }
            }
        },
        400: {
            'description': 'Error en la solicitud o procesamiento del XML',
            'content': {
                'application/json': {
                    'examples': {
                        'template_invalido': {
                            'summary': 'Template no es de tipo XML',
                            'value': {
                                'detail': 'El template seleccionado no es de tipo XML.'
                            }
                        },
                        'xml_invalido': {
                            'summary': 'Archivo XML inválido',
                            'value': {
                                'detail': 'El archivo no es un XML válido: error de sintaxis XML'
                            }
                        },
                        'error_procesamiento': {
                            'summary': 'Error durante el procesamiento',
                            'value': {
                                'detail': 'Error durante el procesamiento del archivo XML.'
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Recurso no encontrado',
            'content': {
                'application/json': {
                    'examples': {
                        'template_no_encontrado': {
                            'summary': 'Template no existe o está inactivo',
                            'value': {
                                'detail': 'No se encontró el template con ID 42 o no está activo.'
                            }
                        },
                        'catalogo_no_encontrado': {
                            'summary': 'Catálogo no existe o no pertenece al proveedor',
                            'value': {
                                'detail': 'No se encontró el catálogo con ID 15 para el proveedor del template.'
                            }
                        }
                    }
                }
            }
        },
    }
)