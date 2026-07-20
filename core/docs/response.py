# core/docs/responses.py
from drf_spectacular.utils import OpenApiResponse, OpenApiExample
from core.responses.messages import AuthMessages, DatabaseMessages, ErrorMessages, ValidationMessages
from core.api_response.error_codes import ErrorCodes
from core.docs.serializers import ApiErrorSerializer, ApiValidationErrorSerializer


def simple_detail_response(example):
    return {
        200: {
            "type": "object",
            "properties": {
                "detail": {
                    "type": "string",
                    "example": example
                }
            }
        }
    }


def _api_error_response(description: str, detail: str, code: str, source: str = "") -> OpenApiResponse:
    return OpenApiResponse(
        response=ApiErrorSerializer,
        description=description,
        examples=[
            OpenApiExample(
                description,
                value={
                    "success": False,
                    "data": None,
                    "message": None,
                    "errors": {
                        "code": code,
                        "source": source,
                        "context": {"detail": detail},
                    },
                }
            )
        ]
    )


def _build_infra_response(description: str, detail: str, code: str) -> dict:
    return {
        "description": description,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "data": None,
                    "message": None,
                    "errors": {
                        "code": code,
                        "source": "",
                        "context": {"detail": detail},
                    },
                }
            }
        }
    }


# ── Infraestructura (hook global) ─────────────────────────────────────────────

INFRA_RESPONSES = {
    "500": _build_infra_response("Error inesperado", ErrorMessages.UNEXPECTED_ERROR, ErrorCodes.UNEXPECTED_ERROR),
    "502": _build_infra_response("Error en API externa", ErrorMessages.EXTERNAL_API_ERROR, ErrorCodes.EXTERNAL_API_ERROR),
    "503": _build_infra_response("Servicio no disponible", ErrorMessages.SERVICE_UNAVAILABLE, ErrorCodes.SERVICE_UNAVAILABLE),
    "504": _build_infra_response("Timeout con servicio externo", ErrorMessages.SERVICE_TIMEOUT, ErrorCodes.SERVICE_TIMEOUT),
}

# ── Por contrato (decoradores) ────────────────────────────────────────────────
# Nota: 'source' se completa automáticamente vía auto_schema (ver decorator.py),
# por eso aquí queda como parámetro para que el decorador lo inyecte.

RESPONSE_401 = _api_error_response(
    "No autenticado",
    AuthMessages.LOGIN_REQUIRED + " / " + AuthMessages.CREDENTIALS_INVALID,
    ErrorCodes.NOT_AUTHENTICATED,
)

RESPONSE_403 = _api_error_response(
    "Permiso denegado",
    AuthMessages.PERMISSION_DENIED,
    ErrorCodes.PERMISSION_DENIED,
)

RESPONSE_404 = _api_error_response(
    "Recurso no encontrado",
    DatabaseMessages.RESOURCE_NOT_FOUND,
    ErrorCodes.NOT_FOUND,
)

RESPONSE_409 = _api_error_response(
    "Conflicto",
    DatabaseMessages.RESOURCE_EXISTS,
    ErrorCodes.RESOURCE_EXISTS,
)

RESPONSE_422 = _api_error_response(
    "Entidad no procesable",
    ValidationMessages.INVALID_FORMAT,
    ErrorCodes.VALIDATION_ERROR,
)

RESPONSE_400_OAUTH = _api_error_response(
    "Error de autenticación OAuth",
    ErrorMessages.OAUTH_ERROR,
    ErrorCodes.OAUTH_ERROR,
)

def response_401(source: str = "") -> OpenApiResponse:
    return _api_error_response(
        "No autenticado",
        AuthMessages.LOGIN_REQUIRED + " / " + AuthMessages.CREDENTIALS_INVALID,
        ErrorCodes.NOT_AUTHENTICATED,
        source,
    )


def response_403(source: str = "") -> OpenApiResponse:
    return _api_error_response(
        "Permiso denegado",
        AuthMessages.PERMISSION_DENIED,
        ErrorCodes.PERMISSION_DENIED,
        source,
    )


def response_404(source: str = "") -> OpenApiResponse:
    return _api_error_response(
        "Recurso no encontrado",
        DatabaseMessages.RESOURCE_NOT_FOUND,
        ErrorCodes.NOT_FOUND,
        source,
    )


def response_409(source: str = "") -> OpenApiResponse:
    return _api_error_response(
        "Conflicto",
        DatabaseMessages.RESOURCE_EXISTS,
        ErrorCodes.RESOURCE_EXISTS,
        source,
    )


def response_422(source: str = "") -> OpenApiResponse:
    return _api_error_response(
        "Entidad no procesable",
        ValidationMessages.INVALID_FORMAT,
        ErrorCodes.VALIDATION_ERROR,
        source,
    )


def response_400_oauth(source: str = "") -> OpenApiResponse:
    return _api_error_response(
        "Error de autenticación OAuth",
        ErrorMessages.OAUTH_ERROR,
        ErrorCodes.OAUTH_ERROR,
        source,
    )


# ── Validación — estructura diferente ────────────────────────────────────────

def response_400(source: str = "") -> OpenApiResponse:
    return OpenApiResponse(
        response=ApiValidationErrorSerializer,
        description="Error de validación — los campos varían según el endpoint",
        examples=[
            OpenApiExample(
                "Campos inválidos",
                value={
                    "success": False,
                    "data": None,
                    "message": None,
                    "errors": {
                        "code": ErrorCodes.VALIDATION_ERROR,
                        "source": source,
                        "context": {
                            "field_name": ["Mensaje de error del campo."],
                        },
                    },
                }
            )
        ]
    )


def response_429(retry_after_seconds: int, source: str = "") -> OpenApiResponse:
    return OpenApiResponse(
        response=ApiErrorSerializer,
        description="Demasiadas solicitudes — límite excedido",
        examples=[
            OpenApiExample(
                "Rate limit excedido",
                value={
                    "success": False,
                    "data": None,
                    "message": None,
                    "errors": {
                        "code": ErrorCodes.THROTTLED,
                        "source": source,
                        "context": {
                            "detail": "Por favor, espera antes de intentar nuevamente.",
                            "retry_after_seconds": retry_after_seconds,
                        },
                    },
                }
            )
        ]
    )