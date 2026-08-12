# templates/docs/schemas.py
#
# Nota: mismo supuesto que en layouts/docs/schemas.py sobre la ubicación
# de 'response_400' y 'RESPONSE_404'.

# ---------------------------------------------------------------------------
# Template
# ---------------------------------------------------------------------------

from core.docs.response import RESPONSE_404, response_400


TEMPLATE_LIST_SCHEMA = dict(
    tags=["template"],
    summary="Listar templates de un supplier",
    description=(
        "Lista los templates activos de un supplier. Anidado bajo "
        "suppliers/{supplier_pk}/templates/."
    ),
    responses={
        200: {
            "description": "Lista de templates",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 3,
                            "supplier": 1,
                            "layout": 1,
                            "layout_code": "CASA_AZUL",
                            "name": "Factura estándar",
                            "document_type": "xml",
                            "is_active": True,
                        }
                    ]
                }
            },
        },
        404: RESPONSE_404,
    },
)

TEMPLATE_CREATE_SCHEMA = dict(
    tags=["template"],
    summary="Crear template",
    description=(
        "Crea un template para el supplier de la URL. Solo puede existir "
        "un template activo por combinación (supplier, layout, "
        "document_type)."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "layout": {"type": "integer", "example": 1},
                "name": {"type": "string", "example": "Factura estándar"},
                "document_type": {
                    "type": "string",
                    "enum": ["xml", "xlsx"],
                    "example": "xml",
                },
            },
            "required": ["layout", "name", "document_type"],
        }
    },
    responses={
        201: {
            "description": "Template creado",
            "content": {
                "application/json": {
                    "example": {
                        "id": 3,
                        "supplier": 1,
                        "layout": 1,
                        "layout_code": "CASA_AZUL",
                        "name": "Factura estándar",
                        "document_type": "xml",
                        "is_active": True,
                    }
                }
            },
        },
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

TEMPLATE_RETRIEVE_SCHEMA = dict(
    tags=["template"],
    summary="Obtener template",
    description="Obtiene el detalle de un template específico.",
    responses={
        200: {
            "description": "Detalle del template",
            "content": {
                "application/json": {
                    "example": {
                        "id": 3,
                        "supplier": 1,
                        "layout": 1,
                        "layout_code": "CASA_AZUL",
                        "name": "Factura estándar",
                        "document_type": "xml",
                        "is_active": True,
                    }
                }
            },
        },
        404: RESPONSE_404,
    },
)

TEMPLATE_UPDATE_SCHEMA = dict(
    tags=["template"],
    summary="Actualizar template",
    description="Reemplaza los datos de un template existente.",
    responses={
        200: {"description": "Template actualizado", "content": {"application/json": {"example": {}}}},
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

TEMPLATE_PARTIAL_UPDATE_SCHEMA = dict(
    tags=["template"],
    summary="Actualizar parcialmente un template",
    description="Actualiza uno o más campos de un template existente.",
    responses={
        200: {"description": "Template actualizado", "content": {"application/json": {"example": {}}}},
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

TEMPLATE_DESTROY_SCHEMA = dict(
    tags=["template"],
    summary="Eliminar template",
    description="Baja lógica del template (BaseModel maneja `is_active`).",
    responses={
        204: {"description": "Template eliminado"},
        404: RESPONSE_404,
    },
)

# ---------------------------------------------------------------------------
# TemplateField
# ---------------------------------------------------------------------------

TEMPLATE_FIELD_LIST_SCHEMA = dict(
    tags=["template"],
    summary="Listar campos mapeados de un template",
    description=(
        "Lista los TemplateField de un template, ordenados por "
        "layout_field.sort_order, incluyendo la cadena de reglas "
        "de normalización de cada uno."
    ),
    responses={
        200: {
            "description": "Lista de campos mapeados",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 20,
                            "template": 3,
                            "layout_field": 10,
                            "layout_field_name": "supplier_code",
                            "source_field": "Proveedor",
                            "extraction_type": "header_name",
                            "worksheet": "",
                            "header_occurrence": 1,
                            "rules": [
                                {
                                    "id": 5,
                                    "template_field": 20,
                                    "normalization_rule": 1,
                                    "normalization_rule_name": "trim_espacios",
                                    "sort_order": 1,
                                }
                            ],
                        }
                    ]
                }
            },
        },
        404: RESPONSE_404,
    },
)

TEMPLATE_FIELD_CREATE_SCHEMA = dict(
    tags=["template"],
    summary="Mapear un campo del template",
    description=(
        "Crea un TemplateField dentro del template de la URL. "
        "`layout_field` debe pertenecer al layout del template; de lo "
        "contrario se rechaza con 400. `worksheet` aplica solo si el "
        "template es de tipo `xlsx`."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "layout_field": {"type": "integer", "example": 10},
                "source_field": {"type": "string", "example": "Proveedor"},
                "extraction_type": {
                    "type": "string",
                    "enum": ["header_name", "xpath"],
                    "example": "header_name",
                },
                "worksheet": {"type": "string", "example": "Hoja1"},
                "header_occurrence": {"type": "integer", "example": 1},
            },
            "required": ["layout_field", "source_field", "extraction_type"],
        }
    },
    responses={
        201: {
            "description": "Campo mapeado",
            "content": {
                "application/json": {
                    "example": {
                        "id": 20,
                        "template": 3,
                        "layout_field": 10,
                        "layout_field_name": "supplier_code",
                        "source_field": "Proveedor",
                        "extraction_type": "header_name",
                        "worksheet": "",
                        "header_occurrence": 1,
                        "rules": [],
                    }
                }
            },
        },
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

TEMPLATE_FIELD_RETRIEVE_SCHEMA = dict(
    tags=["template"],
    summary="Obtener campo mapeado",
    description="Obtiene el detalle de un TemplateField, con su cadena de reglas.",
    responses={
        200: {"description": "Detalle del campo mapeado", "content": {"application/json": {"example": {}}}},
        404: RESPONSE_404,
    },
)

TEMPLATE_FIELD_UPDATE_SCHEMA = dict(
    tags=["template"],
    summary="Actualizar campo mapeado",
    description="Reemplaza los datos de un TemplateField existente.",
    responses={
        200: {"description": "Campo actualizado", "content": {"application/json": {"example": {}}}},
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

TEMPLATE_FIELD_PARTIAL_UPDATE_SCHEMA = dict(
    tags=["template"],
    summary="Actualizar parcialmente un campo mapeado",
    description="Actualiza uno o más campos de un TemplateField existente.",
    responses={
        200: {"description": "Campo actualizado", "content": {"application/json": {"example": {}}}},
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

TEMPLATE_FIELD_DESTROY_SCHEMA = dict(
    tags=["template"],
    summary="Eliminar campo mapeado",
    description="Baja lógica del TemplateField (elimina también su cadena de reglas vía CASCADE).",
    responses={
        204: {"description": "Campo eliminado"},
        404: RESPONSE_404,
    },
)

# ---------------------------------------------------------------------------
# TemplateFieldRule
# ---------------------------------------------------------------------------

TEMPLATE_FIELD_RULE_LIST_SCHEMA = dict(
    tags=["template"],
    summary="Listar reglas de un campo mapeado",
    description=(
        "Lista la cadena de NormalizationRule encadenadas a un "
        "TemplateField, ordenadas por `sort_order` (orden de ejecución)."
    ),
    responses={
        200: {
            "description": "Lista de reglas",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 5,
                            "template_field": 20,
                            "normalization_rule": 1,
                            "normalization_rule_name": "trim_espacios",
                            "sort_order": 1,
                        },
                        {
                            "id": 6,
                            "template_field": 20,
                            "normalization_rule": 2,
                            "normalization_rule_name": "uppercase",
                            "sort_order": 2,
                        },
                    ]
                }
            },
        },
        404: RESPONSE_404,
    },
)

TEMPLATE_FIELD_RULE_CREATE_SCHEMA = dict(
    tags=["template"],
    summary="Encadenar una regla a un campo mapeado",
    description=(
        "Agrega una NormalizationRule a la cadena de un TemplateField, "
        "con su `sort_order` de ejecución. La combinación "
        "(template_field, normalization_rule) debe ser única."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "normalization_rule": {"type": "integer", "example": 1},
                "sort_order": {"type": "integer", "example": 1},
            },
            "required": ["normalization_rule", "sort_order"],
        }
    },
    responses={
        201: {
            "description": "Regla encadenada",
            "content": {
                "application/json": {
                    "example": {
                        "id": 5,
                        "template_field": 20,
                        "normalization_rule": 1,
                        "normalization_rule_name": "trim_espacios",
                        "sort_order": 1,
                    }
                }
            },
        },
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

TEMPLATE_FIELD_RULE_RETRIEVE_SCHEMA = dict(
    tags=["template"],
    summary="Obtener regla encadenada",
    description="Obtiene el detalle de un TemplateFieldRule específico.",
    responses={
        200: {"description": "Detalle de la regla encadenada", "content": {"application/json": {"example": {}}}},
        404: RESPONSE_404,
    },
)

TEMPLATE_FIELD_RULE_UPDATE_SCHEMA = dict(
    tags=["template"],
    summary="Actualizar regla encadenada",
    description="Reemplaza `normalization_rule` y/o `sort_order` de un TemplateFieldRule.",
    responses={
        200: {"description": "Regla actualizada", "content": {"application/json": {"example": {}}}},
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

TEMPLATE_FIELD_RULE_PARTIAL_UPDATE_SCHEMA = dict(
    tags=["template"],
    summary="Actualizar parcialmente una regla encadenada",
    description="Actualiza uno o más campos de un TemplateFieldRule existente.",
    responses={
        200: {"description": "Regla actualizada", "content": {"application/json": {"example": {}}}},
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)

TEMPLATE_FIELD_RULE_DESTROY_SCHEMA = dict(
    tags=["template"],
    summary="Quitar una regla de la cadena",
    description="Elimina (baja lógica) un TemplateFieldRule, sacando esa regla de la cadena del campo.",
    responses={
        204: {"description": "Regla removida de la cadena"},
        404: RESPONSE_404,
    },
)

TEMPLATE_FIELD_RULE_REORDER_SCHEMA = dict(
    tags=["template"],
    summary="Reordenar la cadena de reglas de un campo",
    description=(
        "Recibe una lista ordenada de IDs de TemplateFieldRule "
        "pertenecientes a este template_field y reasigna `sort_order` "
        "según la posición en la lista (1-indexed, orden de ejecución)."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "order": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "example": [6, 5],
                }
            },
            "required": ["order"],
        }
    },
    responses={
        200: {
            "description": "Cadena reordenada",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 6,
                            "template_field": 20,
                            "normalization_rule": 2,
                            "normalization_rule_name": "uppercase",
                            "sort_order": 1,
                        },
                        {
                            "id": 5,
                            "template_field": 20,
                            "normalization_rule": 1,
                            "normalization_rule_name": "trim_espacios",
                            "sort_order": 2,
                        },
                    ]
                }
            },
        },
        400: lambda source: response_400(source),
        404: RESPONSE_404,
    },
)