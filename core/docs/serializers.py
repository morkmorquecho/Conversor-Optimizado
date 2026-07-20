# core/docs/serializers.py
from rest_framework import serializers


class ValidationContextSerializer(serializers.Serializer):
    """
    Contexto de errores de validación DRF.
    Los keys son los campos del serializer que fallaron.
    """
    username = serializers.ListField(child=serializers.CharField(), required=False)
    field_name = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Representa cualquier campo del serializer (email, password, etc.)"
    )


class DetailContextSerializer(serializers.Serializer):
    """Contexto para errores simples (no validación)."""
    detail = serializers.CharField()


class ErrorsValidationSerializer(serializers.Serializer):
    code = serializers.CharField(
        help_text="Código estable del tipo de error, ej. VALIDATION_ERROR"
    )
    source = serializers.CharField(
        help_text="Módulo y vista donde se originó el error (solo trazabilidad, no usar como lógica de negocio)"
    )
    context = ValidationContextSerializer()


class ErrorsDetailSerializer(serializers.Serializer):
    code = serializers.CharField(
        help_text="Código estable del tipo de error, ej. AUTHENTICATION_FAILED"
    )
    source = serializers.CharField(
        help_text="Módulo y vista donde se originó el error (solo trazabilidad, no usar como lógica de negocio)"
    )
    context = DetailContextSerializer()


class ApiValidationErrorSerializer(serializers.Serializer):
    """Estructura para errores de validación (campos inválidos)."""
    success = serializers.BooleanField(default=False)
    data = serializers.JSONField(allow_null=True, default=None)
    message = serializers.CharField(allow_null=True, default=None)
    errors = ErrorsValidationSerializer()


class ApiErrorSerializer(serializers.Serializer):
    """Estructura para cualquier otro error (401, 403, 404, 500...)."""
    success = serializers.BooleanField(default=False)
    data = serializers.JSONField(allow_null=True, default=None)
    message = serializers.CharField(allow_null=True, default=None)
    errors = ErrorsDetailSerializer()