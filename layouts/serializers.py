from rest_framework import serializers

from .models import Layout, LayoutField, NormalizationRule


class LayoutFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = LayoutField
        fields = ["id", "layout", "name", "sort_order", "system_field_key"]
        read_only_fields = ["id", "layout"]


class LayoutSerializer(serializers.ModelSerializer):
    """Serializer plano, usado en 'list' (sin traer todos los fields)."""

    class Meta:
        model = Layout
        fields = ["id", "code", "name"]
        read_only_fields = ["id"]


class LayoutDetailSerializer(serializers.ModelSerializer):
    """Serializer usado en 'retrieve', incluye los LayoutField del layout."""

    layout_fields = LayoutFieldSerializer(source="fields", many=True, read_only=True)

    class Meta:
        model = Layout
        fields = ["id", "code", "name", "layout_fields"]
        read_only_fields = ["id", "layout_fields"]


class NormalizationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormalizationRule
        fields = ["id", "name", "description", "rule_type", "config"]
        read_only_fields = ["id"]