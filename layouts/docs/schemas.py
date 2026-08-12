# layouts/docs/schemas.py
#
# Nota: se asume que 'response_400' y 'RESPONSE_404' viven en
# core.docs.schema_utils (mismo lugar de donde catalogs/docs/schemas.py
# los importa). Ajustar el import si el proyecto los expone en otro módulo.

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

from core.docs.response import RESPONSE_404, response_400


LAYOUT_LIST_SCHEMA = dict(
    tags=["layout"],
    summary="Listar layouts",
    description="Obtiene todos los layouts activos (Casa Azul, Casa Roja, ...).",
    responses={
        200: {
            "description": "Lista de layouts",
            "content": {
                "application/json": {
                    "example": [
                        {"id": 1, "code": "CASA_AZUL", "name": "Casa Azul"},
                        {"id": 2, "code": "CASA_ROJA", "name": "Casa Roja"},
                    ]
                }
            },
        },
        400: lambda source: response_400(source),
    },
)

LAYOUT_RETRIEVE_SCHEMA = dict(
    tags=["layout"],
    summary="Obtener layout con sus campos",
    description=(
        "Obtiene el detalle de un layout, incluyendo la lista de "
        "LayoutField (`layout_fields`) ordenados por `sort_order`."
    ),
    responses={
        200: {
            "description": "Detalle del layout",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "code": "CASA_AZUL",
                        "name": "Casa Azul",
                        "layout_fields": [
                            {"id": 10, "layout": 1, "name": "supplier_code", "sort_order": 1},
                            {"id": 11, "layout": 1, "name": "invoice_date", "sort_order": 2},
                        ],
                    }
                }
            },
        },
        404: RESPONSE_404,
    },
)

LAYOUT_CREATE_SCHEMA = dict(
    tags=["layout"],
    summary="Crear layout",
    description="Crea un nuevo layout destino. `code` debe ser único.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "example": "CASA_AZUL"},
                "name": {"type": "string", "example": "Casa Azul"},
            },
            "required": ["code", "name"],
        }
    },
    responses={
        201: {
            "description": "Layout creado",
            "content": {
                "application/json": {
                    "example": {"id": 1, "code": "CASA_AZUL", "name": "Casa Azul"}
                }
            },
        },
        400: lambda source: response_400(source),
    },
)

LAYOUT_UPDATE_SCHEMA = dict(
    tags=["layout"],
    summary="Actualizar layout",
    description="Reemplaza `code` y `name` de un layout existente.",
    responses={
        200: {
            "description": "Layout actualizado",
            "content": {
                "application/json": {
                    "example": {"id": 1, "code": "CASA_AZUL", "name": "Casa Azul V2"}
                }
            },
        },
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

LAYOUT_PARTIAL_UPDATE_SCHEMA = dict(
    tags=["layout"],
    summary="Actualizar parcialmente un layout",
    description="Actualiza uno o más campos de un layout existente.",
    responses={
        200: {
            "description": "Layout actualizado",
            "content": {
                "application/json": {
                    "example": {"id": 1, "code": "CASA_AZUL", "name": "Casa Azul V2"}
                }
            },
        },
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

LAYOUT_DESTROY_SCHEMA = dict(
    tags=["layout"],
    summary="Eliminar layout",
    description=(
        "Baja lógica del layout (BaseModel maneja `is_active`). No se "
        "permite si hay Templates activos apuntando a este layout "
        "(FK con on_delete=PROTECT en Template.layout)."
    ),
    responses={
        204: {"description": "Layout eliminado"},
        404: RESPONSE_404,
    },
)

# ---------------------------------------------------------------------------
# LayoutField
# ---------------------------------------------------------------------------

LAYOUT_FIELD_LIST_SCHEMA = dict(
    tags=["layout"],
    summary="Listar campos de un layout",
    description="Lista los LayoutField de un layout, ordenados por `sort_order`.",
    responses={
        200: {
            "description": "Lista de campos",
            "content": {
                "application/json": {
                    "example": [
                        {"id": 10, "layout": 1, "name": "supplier_code", "sort_order": 1},
                        {"id": 11, "layout": 1, "name": "invoice_date", "sort_order": 2},
                    ]
                }
            },
        },
        404: RESPONSE_404,
    },
)

LAYOUT_FIELD_CREATE_SCHEMA = dict(
    tags=["layout"],
    summary="Crear campo de layout",
    description=(
        "Crea un LayoutField dentro del layout de la URL. `name` y "
        "`sort_order` deben ser únicos dentro del layout."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "example": "invoice_date"},
                "sort_order": {"type": "integer", "example": 2},
            },
            "required": ["name", "sort_order"],
        }
    },
    responses={
        201: {
            "description": "Campo creado",
            "content": {
                "application/json": {
                    "example": {"id": 11, "layout": 1, "name": "invoice_date", "sort_order": 2}
                }
            },
        },
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

LAYOUT_FIELD_RETRIEVE_SCHEMA = dict(
    tags=["layout"],
    summary="Obtener campo de layout",
    description="Obtiene el detalle de un LayoutField específico.",
    responses={
        200: {
            "description": "Detalle del campo",
            "content": {
                "application/json": {
                    "example": {"id": 11, "layout": 1, "name": "invoice_date", "sort_order": 2}
                }
            },
        },
        404: RESPONSE_404,
    },
)

LAYOUT_FIELD_UPDATE_SCHEMA = dict(
    tags=["layout"],
    summary="Actualizar campo de layout",
    description="Reemplaza `name` y `sort_order` de un LayoutField.",
    responses={
        200: {
            "description": "Campo actualizado",
            "content": {"application/json": {"example": {"id": 11, "layout": 1, "name": "invoice_date", "sort_order": 3}}},
        },
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

LAYOUT_FIELD_PARTIAL_UPDATE_SCHEMA = dict(
    tags=["layout"],
    summary="Actualizar parcialmente un campo de layout",
    description="Actualiza uno o más campos de un LayoutField existente.",
    responses={
        200: {
            "description": "Campo actualizado",
            "content": {"application/json": {"example": {"id": 11, "layout": 1, "name": "invoice_date", "sort_order": 3}}},
        },
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

LAYOUT_FIELD_DESTROY_SCHEMA = dict(
    tags=["layout"],
    summary="Eliminar campo de layout",
    description=(
        "Baja lógica del campo. No se permite si hay TemplateField "
        "apuntando a este LayoutField (FK con on_delete=PROTECT)."
    ),
    responses={
        204: {"description": "Campo eliminado"},
        404: RESPONSE_404,
    },
)

LAYOUT_FIELD_REORDER_SCHEMA = dict(
    tags=["layout"],
    summary="Reordenar campos de un layout",
    description=(
        "Recibe una lista ordenada de IDs de LayoutField pertenecientes a "
        "este layout y reasigna `sort_order` según la posición en la lista "
        "(1-indexed). Todos los IDs deben pertenecer al layout de la URL."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "order": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "example": [11, 10, 12],
                }
            },
            "required": ["order"],
        }
    },
    responses={
        200: {
            "description": "Campos reordenados",
            "content": {
                "application/json": {
                    "example": [
                        {"id": 11, "layout": 1, "name": "invoice_date", "sort_order": 1},
                        {"id": 10, "layout": 1, "name": "supplier_code", "sort_order": 2},
                        {"id": 12, "layout": 1, "name": "total", "sort_order": 3},
                    ]
                }
            },
        },
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

# ---------------------------------------------------------------------------
# NormalizationRule
# ---------------------------------------------------------------------------

NORMALIZATION_RULE_LIST_SCHEMA = dict(
    tags=["normalization-rule"],
    summary="Listar reglas de normalización",
    description="Lista todas las reglas de normalización activas, reutilizables entre templates.",
    responses={
        200: {
            "description": "Lista de reglas",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "name": "fecha_dd_mm_yyyy",
                            "description": "Normaliza fechas a dd/mm/yyyy",
                            "rule_type": "date_format",
                            "config": {"input_format": "%Y-%m-%d", "output_format": "%d/%m/%Y"},
                        }
                    ]
                }
            },
        },
        400: lambda source: response_400(source),
    },
)

NORMALIZATION_RULE_CREATE_SCHEMA = dict(
    tags=["normalization-rule"],
    summary="Crear regla de normalización",
    description=(
        "Crea una regla de normalización. `name` debe ser único. `config` "
        "varía según `rule_type` (por ejemplo, `value_map` espera un "
        "diccionario de mapeo; `regex_replace` espera `pattern`/`replacement`)."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "example": "fecha_dd_mm_yyyy"},
                "description": {"type": "string", "example": "Normaliza fechas a dd/mm/yyyy"},
                "rule_type": {
                    "type": "string",
                    "enum": ["date_format", "value_map", "regex_replace", "trim", "uppercase"],
                    "example": "date_format",
                },
                "config": {
                    "type": "object",
                    "example": {"input_format": "%Y-%m-%d", "output_format": "%d/%m/%Y"},
                },
            },
            "required": ["name", "rule_type"],
        }
    },
    responses={
        201: {
            "description": "Regla creada",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "fecha_dd_mm_yyyy",
                        "description": "Normaliza fechas a dd/mm/yyyy",
                        "rule_type": "date_format",
                        "config": {"input_format": "%Y-%m-%d", "output_format": "%d/%m/%Y"},
                    }
                }
            },
        },
        400: lambda source: response_400(source),
    },
)

NORMALIZATION_RULE_RETRIEVE_SCHEMA = dict(
    tags=["normalization-rule"],
    summary="Obtener regla de normalización",
    description="Obtiene el detalle de una regla de normalización.",
    responses={
        200: {
            "description": "Detalle de la regla",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "fecha_dd_mm_yyyy",
                        "description": "Normaliza fechas a dd/mm/yyyy",
                        "rule_type": "date_format",
                        "config": {"input_format": "%Y-%m-%d", "output_format": "%d/%m/%Y"},
                    }
                }
            },
        },
        404: RESPONSE_404,
    },
)

NORMALIZATION_RULE_UPDATE_SCHEMA = dict(
    tags=["normalization-rule"],
    summary="Actualizar regla de normalización",
    description="Reemplaza los datos de una regla de normalización existente.",
    responses={
        200: {"description": "Regla actualizada", "content": {"application/json": {"example": {}}}},
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

NORMALIZATION_RULE_PARTIAL_UPDATE_SCHEMA = dict(
    tags=["normalization-rule"],
    summary="Actualizar parcialmente una regla de normalización",
    description="Actualiza uno o más campos de una regla de normalización.",
    responses={
        200: {"description": "Regla actualizada", "content": {"application/json": {"example": {}}}},
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

NORMALIZATION_RULE_DESTROY_SCHEMA = dict(
    tags=["normalization-rule"],
    summary="Eliminar regla de normalización",
    description=(
        "Baja lógica de la regla. No se permite si hay TemplateFieldRule "
        "apuntando a esta regla (FK con on_delete=PROTECT)."
    ),
    responses={
        204: {"description": "Regla eliminada"},
        404: RESPONSE_404,
    },
)