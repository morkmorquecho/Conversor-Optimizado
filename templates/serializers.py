from rest_framework import serializers

from .models import Template, TemplateField, TemplateFieldRule


class TemplateSerializer(serializers.ModelSerializer):
    layout_code = serializers.CharField(source="layout.code", read_only=True)

    class Meta:
        model = Template
        fields = [
            "id",
            "supplier",
            "layout",
            "layout_code",
            "name",
            "document_type",
            "is_active",
        ]
        read_only_fields = ["id", "supplier", "layout_code"]


class TemplateFieldRuleSerializer(serializers.ModelSerializer):
    normalization_rule_name = serializers.CharField(
        source="normalization_rule.name", read_only=True
    )

    class Meta:
        model = TemplateFieldRule
        fields = [
            "id",
            "template_field",
            "normalization_rule",
            "normalization_rule_name",
            "sort_order",
        ]
        read_only_fields = ["id", "template_field"]


class TemplateFieldSerializer(serializers.ModelSerializer):
    """Serializer principal de TemplateField.

    Incluye la cadena de reglas de normalización (solo lectura; se
    administran vía TemplateFieldRuleViewSet, anidado bajo este recurso)
    y valida que el layout_field pertenezca al layout del template
    (misma regla que TemplateField.clean()), usando el 'template' pasado
    en el contexto por la vista.
    """

    rules = TemplateFieldRuleSerializer(many=True, read_only=True)
    layout_field_name = serializers.CharField(
        source="layout_field.name", read_only=True
    )

    class Meta:
        model = TemplateField
        fields = [
            "id",
            "template",
            "layout_field",
            "layout_field_name",
            "source_field",
            "extraction_type",
            "worksheet",
            "header_occurrence",
            "rules",
        ]
        read_only_fields = ["id", "template", "layout_field_name", "rules"]

    def validate_layout_field(self, layout_field):
        template = self.context.get("template")
        if template and layout_field.layout_id != template.layout_id:
            raise serializers.ValidationError(
                "layout_field debe pertenecer al mismo layout que el template."
            )
        return layout_field 