from drf_spectacular.utils import OpenApiResponse
from rest_framework import status

from core.responses.messages import AuthMessages, UserMessages

class UserResponses:
    """Schemas de respuesta para documentación"""
    
    CREATED_201 = {
        201: OpenApiResponse(description=UserMessages.USER_CREATED),
        400: OpenApiResponse(description="Datos inválidos")
    }
    
    VERIFIED_200 = {
        200: OpenApiResponse(description=UserMessages.USER_VERIFIED),
        400: OpenApiResponse(description=AuthMessages.TOKEN_NOT_PROVIDED),
        401: OpenApiResponse(description=AuthMessages.TOKEN_INVALID_OR_EXPIRED),
        404: OpenApiResponse(description=UserMessages.USER_NOT_FOUND),
        409: OpenApiResponse(description=UserMessages.USER_ALREADY_VERIFIED)
    }
    
    ACTIVATION_200 = {
        200: OpenApiResponse(description="Usuario activado/desactivado"),
    }