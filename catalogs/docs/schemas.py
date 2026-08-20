from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiExample
from catalogs.serializers import SupplierCatalogDetailSerializer, SupplierCatalogRowSerializer, SupplierCatalogSerializer, SupplierSerializer
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
        
        404: RESPONSE_404,
    }
)


SUPPLIER_LIST_SCHEMA = dict(
    tags=['catalog'],
    summary='Listar proveedores',
    description='Devuelve todos los proveedores registrados.',
    responses={
        200: SupplierSerializer(many=True),
    },
)

# ── SupplierCatalogViewSet ──────────────────────────────────────────────

SUPPLIER_CATALOG_LIST_SCHEMA = dict(
    tags=['catalog'],
    summary='Listar catálogos de un proveedor',
    description=(
        'Devuelve todos los catálogos activos configurados para el proveedor indicado. '
        'Vista resumida: no incluye columnas ni filas, solo metadata.'
    ),
    responses={
        200: SupplierCatalogSerializer(many=True),
    },
)

SUPPLIER_CATALOG_RETRIEVE_SCHEMA = dict(
    tags=['catalog'],
    summary='Detalle de un catálogo',
    description=(
        'Devuelve la información de un catálogo, incluyendo las columnas '
        '(`SupplierCatalogColumn`) configuradas para él. No incluye las filas: '
        'para el contenido usa el endpoint de `rows`.'
    ),
    responses={
        200: SupplierCatalogDetailSerializer,
        404: {
            'description': 'Catálogo no encontrado',
            'content': {
                'application/json': {
                    'example': {'detail': 'No se encontró el catálogo con ID 15 para este proveedor.'}
                }
            }
        },
    },
)

SUPPLIER_CATALOG_CREATE_SCHEMA = dict(
    tags=['catalog'],
    summary='Crear catálogo',
    description=(
        'Crea un nuevo catálogo (`SupplierCatalog`) para el proveedor indicado en la URL. '
        'El `pivot_field_name` debe coincidir con el nombre de columna en el archivo '
        'fuente que se usará como llave de búsqueda (ej. "PART NO").'
    ),
    responses={
        201: SupplierCatalogDetailSerializer,
        400: {
            'description': 'Error de validación',
            'content': {
                'application/json': {
                    'example': {'name': ['This field is required.']}
                }
            }
        },
    },
)

SUPPLIER_CATALOG_UPDATE_SCHEMA = dict(
    tags=['catalog'],
    summary='Actualizar catálogo',
    description='Actualiza el nombre o el `pivot_field_name` de un catálogo existente.',
    responses={
        200: SupplierCatalogDetailSerializer,
        400: {
            'description': 'Error de validación',
            'content': {'application/json': {'example': {'name': ['This field is required.']}}}
        },
        404: {
            'description': 'Catálogo no encontrado',
            'content': {'application/json': {'example': {'detail': 'No se encontró el catálogo con ID 15 para este proveedor.'}}}
        },
    },
)

SUPPLIER_CATALOG_PARTIAL_UPDATE_SCHEMA = dict(
    **{**SUPPLIER_CATALOG_UPDATE_SCHEMA, 'summary': 'Actualizar catálogo parcialmente'}
)

SUPPLIER_CATALOG_DESTROY_SCHEMA = dict(
    tags=['catalog'],
    summary='Eliminar catálogo',
    description=(
        'Elimina (soft-delete vía `is_active`) el catálogo. Sus columnas y filas '
        'asociadas dejan de mostrarse en los listados, pero no se borran físicamente.'
    ),
    responses={
        204: {'description': 'Catálogo eliminado correctamente'},
        404: {
            'description': 'Catálogo no encontrado',
            'content': {'application/json': {'example': {'detail': 'No se encontró el catálogo con ID 15 para este proveedor.'}}}
        },
    },
)


# ── SupplierCatalogRowViewSet ───────────────────────────────────────────

SUPPLIER_CATALOG_ROW_LIST_SCHEMA = dict(
    tags=['catalog'],
    summary='Listar filas de un catálogo',
    description=(
        'Devuelve todas las filas (`SupplierCatalogRow`) del catálogo indicado. '
        'Cada fila representa un registro de referencia (ej. fracción arancelaria por '
        'número de parte), identificado por `pivot_value` y con los datos de columna '
        'en `data` (formato `source_name -> valor`).'
    ),
    responses={
        200: SupplierCatalogRowSerializer(many=True),
    },
)

SUPPLIER_CATALOG_ROW_RETRIEVE_SCHEMA = dict(
    tags=['catalog'],
    summary='Detalle de una fila del catálogo',
    responses={
        200: SupplierCatalogRowSerializer,
        404: {
            'description': 'Fila no encontrada',
            'content': {'application/json': {'example': {'detail': 'No se encontró la fila con ID 200 en este catálogo.'}}}
        },
    },
)

SUPPLIER_CATALOG_ROW_CREATE_SCHEMA = dict(
    tags=['catalog'],
    summary='Agregar fila al catálogo',
    description=(
        'Crea una fila nueva. `pivot_value` debe ser único dentro del catálogo '
        '(`unique_pivot_value_per_catalog`); si ya existe, la petición falla con 400.'
    ),
    responses={
        201: SupplierCatalogRowSerializer,
        400: {
            'description': 'Error de validación',
            'content': {
                'application/json': {
                    'example': {'pivot_value': ['Ya existe una fila con este valor pivote en el catálogo.']}
                }
            }
        },
    },
)

SUPPLIER_CATALOG_ROW_UPDATE_SCHEMA = dict(
    tags=['catalog'],
    summary='Actualizar fila del catálogo',
    description='Reemplaza `pivot_value` y/o `data` de una fila existente.',
    responses={
        200: SupplierCatalogRowSerializer,
        400: {
            'description': 'Error de validación',
            'content': {
                'application/json': {
                    'example': {'pivot_value': ['Ya existe una fila con este valor pivote en el catálogo.']}
                }
            }
        },
        404: {
            'description': 'Fila no encontrada',
            'content': {'application/json': {'example': {'detail': 'No se encontró la fila con ID 200 en este catálogo.'}}}
        },
    },
)

SUPPLIER_CATALOG_ROW_PARTIAL_UPDATE_SCHEMA = dict(
    **{**SUPPLIER_CATALOG_ROW_UPDATE_SCHEMA, 'summary': 'Actualizar fila parcialmente'}
)

SUPPLIER_CATALOG_ROW_DESTROY_SCHEMA = dict(
    tags=['catalog'],
    summary='Eliminar fila del catálogo',
    responses={
        204: {'description': 'Fila eliminada correctamente'},
        404: {
            'description': 'Fila no encontrada',
            'content': {'application/json': {'example': {'detail': 'No se encontró la fila con ID 200 en este catálogo.'}}}
        },
    },
)


SUPPLIER_CATALOG_PIVOT_MAPPING_LIST_SCHEMA = dict(
    tags=["catalog"],
    summary="Listar mapeos de campos pivote",
    description=(
        "Obtiene los mapeos de campos pivote configurados para un catálogo "
        "específico de un proveedor."
    ),
    responses={
        200: {
            "description": "Lista de mapeos de campos pivote",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "integer",
                                },
                                "template": {
                                    "type": "integer",
                                },
                                "pivot_template_field": {
                                    "type": "integer",
                                },
                            },
                        },
                    }
                }
            },
        },
        404: RESPONSE_404,
    },
)


SUPPLIER_CATALOG_PIVOT_MAPPING_RETRIEVE_SCHEMA = dict(
    tags=["catalog"],
    summary="Obtener mapeo de campo pivote",
    description=(
        "Obtiene un mapeo de campo pivote específico por su ID dentro "
        "del catálogo indicado."
    ),
    responses={
        200: {
            "description": "Detalle del mapeo de campo pivote",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer",
                            },
                            "template": {
                                "type": "integer",
                            },
                            "pivot_template_field": {
                                "type": "integer",
                            },
                        },
                    }
                }
            },
        },
        404: RESPONSE_404,
    },
)


SUPPLIER_CATALOG_PIVOT_MAPPING_CREATE_SCHEMA = dict(
    tags=["catalog"],
    summary="Crear mapeo de campo pivote",
    description=(
        "Crea un mapeo entre un Template y un TemplateField que será "
        "utilizado como campo pivote para el catálogo indicado.\n\n"
        "El template seleccionado debe pertenecer al mismo proveedor "
        "que el catálogo. Además, el pivot_template_field debe "
        "pertenecer al template indicado."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "template": {
                    "type": "integer",
                    "description": "ID del template.",
                },
                "pivot_template_field": {
                    "type": "integer",
                    "description": "ID del campo del template utilizado como pivote.",
                },
            },
            "required": [
                "template",
                "pivot_template_field",
            ],
        }
    },
    responses={
        201: {
            "description": "Mapeo de campo pivote creado",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer",
                            },
                            "template": {
                                "type": "integer",
                            },
                            "pivot_template_field": {
                                "type": "integer",
                            },
                        },
                    }
                }
            },
        },
        400: {
            "description": "Datos de la solicitud inválidos",
            "content": {
                "application/json": {
                    "examples": {
                        "pivot_field_template_mismatch": {
                            "summary": "Campo pivote de otro template",
                            "value": {
                                "pivot_template_field": [
                                    "Debe pertenecer al template indicado."
                                ]
                            },
                        }
                    }
                }
            },
        },
        404: RESPONSE_404,
    },
)


SUPPLIER_CATALOG_PIVOT_MAPPING_UPDATE_SCHEMA = dict(
    tags=["catalog"],
    summary="Actualizar mapeo de campo pivote",
    description=(
        "Actualiza completamente un mapeo de campo pivote existente.\n\n"
        "El pivot_template_field debe pertenecer al template indicado."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "template": {
                    "type": "integer",
                    "description": "ID del template.",
                },
                "pivot_template_field": {
                    "type": "integer",
                    "description": "ID del campo del template utilizado como pivote.",
                },
            },
            "required": [
                "template",
                "pivot_template_field",
            ],
        }
    },
    responses={
        200: {
            "description": "Mapeo de campo pivote actualizado",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer",
                            },
                            "template": {
                                "type": "integer",
                            },
                            "pivot_template_field": {
                                "type": "integer",
                            },
                        },
                    }
                }
            },
        },
        400: {
            "description": "Datos de la solicitud inválidos",
            "content": {
                "application/json": {
                    "examples": {
                        "pivot_field_template_mismatch": {
                            "summary": "Campo pivote de otro template",
                            "value": {
                                "pivot_template_field": [
                                    "Debe pertenecer al template indicado."
                                ]
                            },
                        }
                    }
                }
            },
        },
        404: RESPONSE_404,
    },
)


SUPPLIER_CATALOG_PIVOT_MAPPING_PARTIAL_UPDATE_SCHEMA = dict(
    tags=["catalog"],
    summary="Actualizar parcialmente mapeo de campo pivote",
    description=(
        "Actualiza parcialmente un mapeo de campo pivote existente. "
        "Si se proporcionan ambos campos, el pivot_template_field debe "
        "pertenecer al template indicado."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "template": {
                    "type": "integer",
                    "description": "ID del template.",
                },
                "pivot_template_field": {
                    "type": "integer",
                    "description": "ID del campo del template utilizado como pivote.",
                },
            },
        }
    },
    responses={
        200: {
            "description": "Mapeo de campo pivote actualizado",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer",
                            },
                            "template": {
                                "type": "integer",
                            },
                            "pivot_template_field": {
                                "type": "integer",
                            },
                        },
                    }
                }
            },
        },
        400: {
            "description": "Datos de la solicitud inválidos",
            "content": {
                "application/json": {
                    "examples": {
                        "pivot_field_template_mismatch": {
                            "summary": "Campo pivote de otro template",
                            "value": {
                                "pivot_template_field": [
                                    "Debe pertenecer al template indicado."
                                ]
                            },
                        }
                    }
                }
            },
        },
        404: RESPONSE_404,
    },
)


SUPPLIER_CATALOG_PIVOT_MAPPING_DESTROY_SCHEMA = dict(
    tags=["catalog"],
    summary="Eliminar mapeo de campo pivote",
    description=(
        "Elimina permanentemente el mapeo de campo pivote indicado. "
        "La eliminación utiliza hard delete."
    ),
    responses={
        204: {
            "description": "Mapeo de campo pivote eliminado correctamente.",
        },
        404: RESPONSE_404,
    },
)