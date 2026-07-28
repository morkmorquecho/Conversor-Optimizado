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