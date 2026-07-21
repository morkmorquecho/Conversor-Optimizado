from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiExample
from core.responses.messages import AuthMessages, UserMessages
from core.responses.schemas import UserResponses
from core.docs.response import RESPONSE_400_OAUTH, RESPONSE_401, RESPONSE_404, RESPONSE_409, response_400, response_429

SUPPLIER_CATALOG_ROW_SCHEMA = dict(
    tags=['catalog'],
    summary='Listar filas del catálogo',
    description=(
        'Obtiene todas las filas de un catálogo específico.\n\n'
        '**Parámetros de consulta:**\n'
        '- `supplier_catalog`: ID del catálogo (obligatorio)\n\n'
        'Retorna una lista de objetos `SupplierCatalogRow` con sus datos.'
    ),
    parameters=[
        {
            'name': 'supplier_catalog',
            'in': 'query',
            'required': True,
            'schema': {'type': 'integer'},
            'description': 'ID del catálogo del proveedor'
        }
    ],
    responses={
        200: {
            'description': 'Lista de filas del catálogo',
            'content': {
                'application/json': {
                    'example': [
                        {
                            'id': 1,
                            'supplier_catalog': 5,
                            'pivot_value': 'Producto A',
                            'data': {
                                'precio': '100.50',
                                'stock': '25',
                                'descripcion': 'Producto de ejemplo'
                            },
                            'created_at': '2024-01-15T10:30:00Z',
                            'updated_at': '2024-01-15T10:30:00Z'
                        }
                    ]
                }
            }
        },
        400: lambda source: response_400(source),
        401: RESPONSE_401,
        404: RESPONSE_404,
    }
)

SUPPLIER_CATALOG_ROW_CREATE_SCHEMA = dict(
    tags=['catalog'],
    summary='Crear fila de catálogo',
    description=(
        'Crea una nueva fila en el catálogo especificado.\n\n'
        '**Validaciones:**\n'
        '- El `pivot_value` debe ser único dentro del catálogo\n'
        '- Los campos en `data` deben corresponder a las columnas configuradas\n'
        '- El `supplier_catalog` debe existir'
    ),
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'supplier_catalog': {
                    'type': 'integer',
                    'example': 5,
                    'description': 'ID del catálogo del proveedor'
                },
                'pivot_value': {
                    'type': 'string',
                    'example': 'Producto A',
                    'description': 'Valor único identificador de la fila'
                },
                'data': {
                    'type': 'object',
                    'example': {
                        'precio': '100.50',
                        'stock': '25',
                        'descripcion': 'Producto de ejemplo'
                    },
                    'description': 'Datos de la fila según columnas configuradas'
                }
            },
            'required': ['supplier_catalog', 'pivot_value', 'data']
        }
    },
    responses={
        201: {
            'description': 'Fila creada exitosamente',
            'content': {
                'application/json': {
                    'example': {
                        'id': 1,
                        'supplier_catalog': 5,
                        'pivot_value': 'Producto A',
                        'data': {
                            'precio': '100.50',
                            'stock': '25',
                            'descripcion': 'Producto de ejemplo'
                        },
                        'created_at': '2024-01-15T10:30:00Z',
                        'updated_at': '2024-01-15T10:30:00Z'
                    }
                }
            }
        },
        400: lambda source: response_400(source),
        401: RESPONSE_401,
        404: RESPONSE_404,
    }
)

SUPPLIER_CATALOG_ROW_RETRIEVE_SCHEMA = dict(
    tags=['catalog'],
    summary='Obtener fila específica',
    description=(
        'Obtiene los detalles de una fila específica del catálogo por su ID.'
    ),
    responses={
        200: {
            'description': 'Detalles de la fila',
            'content': {
                'application/json': {
                    'example': {
                        'id': 1,
                        'supplier_catalog': 5,
                        'pivot_value': 'Producto A',
                        'data': {
                            'precio': '100.50',
                            'stock': '25',
                            'descripcion': 'Producto de ejemplo'
                        },
                        'created_at': '2024-01-15T10:30:00Z',
                        'updated_at': '2024-01-15T10:30:00Z'
                    }
                }
            }
        },
        401: RESPONSE_401,
        404: RESPONSE_404,
    }
)

SUPPLIER_CATALOG_ROW_UPDATE_SCHEMA = dict(
    tags=['catalog'],
    summary='Actualizar fila de catálogo',
    description=(
        'Actualiza parcial o completamente una fila existente del catálogo.\n\n'
        '**Validaciones:**\n'
        '- El `pivot_value` debe ser único dentro del catálogo (si se actualiza)\n'
        '- Los campos en `data` deben corresponder a las columnas configuradas'
    ),
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'pivot_value': {
                    'type': 'string',
                    'example': 'Producto A Actualizado',
                    'description': 'Valor único identificador de la fila'
                },
                'data': {
                    'type': 'object',
                    'example': {
                        'precio': '110.75',
                        'stock': '30',
                        'descripcion': 'Producto actualizado'
                    },
                    'description': 'Datos de la fila según columnas configuradas'
                }
            }
        }
    },
    responses={
        200: {
            'description': 'Fila actualizada exitosamente',
            'content': {
                'application/json': {
                    'example': {
                        'id': 1,
                        'supplier_catalog': 5,
                        'pivot_value': 'Producto A Actualizado',
                        'data': {
                            'precio': '110.75',
                            'stock': '30',
                            'descripcion': 'Producto actualizado'
                        },
                        'created_at': '2024-01-15T10:30:00Z',
                        'updated_at': '2024-01-15T10:35:00Z'
                    }
                }
            }
        },
        400: lambda source: response_400(source),
        401: RESPONSE_401,
        404: RESPONSE_404,
    }
)

SUPPLIER_CATALOG_ROW_PARTIAL_UPDATE_SCHEMA = dict(
    tags=['catalog'],
    summary='Actualizar parcialmente fila de catálogo',
    description=(
        'Actualiza parcialmente una fila existente del catálogo.\n\n'
        '**Nota:** Solo se actualizan los campos enviados en la solicitud.'
    ),
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'pivot_value': {
                    'type': 'string',
                    'example': 'Producto A',
                    'description': 'Valor único identificador de la fila'
                },
                'data': {
                    'type': 'object',
                    'example': {
                        'stock': '35'
                    },
                    'description': 'Datos parciales de la fila'
                }
            }
        }
    },
    responses={
        200: {
            'description': 'Fila actualizada parcialmente',
            'content': {
                'application/json': {
                    'example': {
                        'id': 1,
                        'supplier_catalog': 5,
                        'pivot_value': 'Producto A',
                        'data': {
                            'precio': '110.75',
                            'stock': '35',
                            'descripcion': 'Producto actualizado'
                        },
                        'created_at': '2024-01-15T10:30:00Z',
                        'updated_at': '2024-01-15T10:40:00Z'
                    }
                }
            }
        },
        400: lambda source: response_400(source),
        401: RESPONSE_401,
        404: RESPONSE_404,
    }
)

SUPPLIER_CATALOG_ROW_DELETE_SCHEMA = dict(
    tags=['catalog'],
    summary='Eliminar fila de catálogo',
    description=(
        'Elimina una fila específica del catálogo por su ID.\n\n'
        '**Nota:** Esta acción no se puede deshacer.'
    ),
    responses={
        204: {
            'description': 'Fila eliminada exitosamente (sin contenido)'
        },
        401: RESPONSE_401,
        404: RESPONSE_404,
    }
)

SUPPLIER_CATALOG_ROW_UPLOAD_SCHEMA = dict(
    tags=['catalog'],
    summary='Cargar filas masivamente desde Excel',
    description=(
        'Reemplaza completamente las filas de un catálogo desde un archivo Excel.\n\n'
        '**Requisitos del archivo:**\n'
        '- El archivo debe contener la columna pivote (`pivot_field_name` del catálogo)\n'
        '- Debe incluir todas las columnas configuradas (`SupplierCatalogColumn.source_name`)\n'
        '- Los valores de la columna pivote deben ser únicos\n\n'
        '**Proceso:**\n'
        '1. Valida el archivo Excel\n'
        '2. Verifica que todas las columnas requeridas estén presentes\n'
        '3. Comprueba que no haya duplicados en la columna pivote\n'
        '4. Elimina todas las filas existentes del catálogo\n'
        '5. Inserta las nuevas filas en una transacción atómica'
    ),
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'supplier_catalog': {
                    'type': 'integer',
                    'example': 5,
                    'description': 'ID del catálogo del proveedor'
                },
                'file': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Archivo Excel (.xlsx, .xls) con los datos'
                }
            },
            'required': ['supplier_catalog', 'file']
        }
    },
    responses={
        201: {
            'description': 'Catálogo actualizado exitosamente',
            'content': {
                'application/json': {
                    'example': {
                        'created': 150
                    }
                }
            }
        },
        400: {
            'description': 'Error en la solicitud',
            'content': {
                'application/json': {
                    'examples': {
                        'archivo_invalido': {
                            'summary': 'No se pudo leer el archivo',
                            'value': {
                                'detail': 'No se pudo leer el archivo: Error de formato'
                            }
                        },
                        'columnas_faltantes': {
                            'summary': 'Faltan columnas requeridas',
                            'value': {
                                'detail': 'Faltan columnas en el archivo: precio, stock'
                            }
                        },
                        'duplicados': {
                            'summary': 'Valores duplicados en columna pivote',
                            'value': {
                                'detail': 'Valores de pivote duplicados en el archivo: Producto A, Producto B'
                            }
                        }
                    }
                }
            }
        },
        401: RESPONSE_401,
        404: RESPONSE_404,
    }
)

EXCEL_DEDUPLICATE_SCHEMA = dict(
    tags=['catalog'],
    summary='Eliminar duplicados de un catalogo, paso necesario para subir un catalogo',
    description=(
        'Sube un archivo Excel y un catálogo de proveedor, elimina filas vacías y '
        'duplicados usando la columna pivote configurada en el catálogo.\n\n'
        '**Proceso:**\n'
        '1. Lee el archivo Excel y lo convierte a DataFrame\n'
        '2. Valida que la columna pivote configurada exista en el archivo\n'
        '3. Elimina filas completamente vacías (`dropna(how="all")`)\n'
        '4. Elimina filas donde la columna pivote está vacía\n'
        '5. Elimina duplicados basándose en la columna pivote, manteniendo la primera ocurrencia\n'
        '6. Devuelve el archivo procesado listo para descargar\n\n'
        '**Columnas permitidas:**\n'
        '- Cualquier columna puede estar presente en el archivo\n'
        '- La columna pivote se determina automáticamente desde el catálogo\n'
        '- Los valores de la columna pivote deben ser únicos después del procesamiento\n\n'
        '**Formato de respuesta:**\n'
        '- Archivo Excel descargable\n'
        '- Incluye header `X-Duplicates-Removed` con el número de duplicados eliminados'
    ),
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'supplier_catalog': {
                    'type': 'integer',
                    'example': 5,
                    'description': 'ID del catálogo del proveedor que contiene la columna pivote'
                },
                'file': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Archivo Excel (.xlsx, .xls) para procesar'
                }
            },
            'required': ['supplier_catalog', 'file']
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
                        'description': 'Archivo Excel con duplicados eliminados'
                    },
                    'example': None  # Binary file response
                }
            },
            'headers': {
                'Content-Disposition': {
                    'description': 'Nombre del archivo descargado',
                    'schema': {
                        'type': 'string',
                        'example': 'attachment; filename="archivo_sin_duplicados.xlsx"'
                    }
                },
                'X-Duplicates-Removed': {
                    'description': 'Número de filas duplicadas eliminadas',
                    'schema': {
                        'type': 'integer',
                        'example': 5
                    }
                }
            }
        },
        400: {
            'description': 'Error en la solicitud',
            'content': {
                'application/json': {
                    'examples': {
                        'archivo_invalido': {
                            'summary': 'No se pudo leer el archivo',
                            'value': {
                                'code': 'VALIDATION_ERROR',
                                'detail': 'No se pudo leer el archivo: Error de formato'
                            }
                        },
                        'columna_pivote_faltante': {
                            'summary': 'Columna pivote no encontrada',
                            'value': {
                                'code': 'VALIDATION_ERROR',
                                'detail': "El archivo no trae la columna pivote 'codigo_producto' configurada para este catálogo. Columnas disponibles: producto, precio, stock"
                            }
                        }
                    }
                }
            }
        },
        401: RESPONSE_401,
        404: RESPONSE_404,
    }
)


