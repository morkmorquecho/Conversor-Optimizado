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
            "pdf_extraction_mode",
            "line_pattern_hint",
            "is_active",
        ]
        read_only_fields = ["id", "supplier", "layout_code", "name"]

    def validate(self, attrs):
        # Chequeos que NO dependen de pk (los que sí dependen, como
        # "hay fields line_item", se resuelven en Template.clean(),
        # llamado desde la view después del save).
        document_type = attrs.get(
            "document_type", getattr(self.instance, "document_type", None)
        )
        pdf_extraction_mode = attrs.get(
            "pdf_extraction_mode", getattr(self.instance, "pdf_extraction_mode", "")
        )
        line_pattern_hint = attrs.get(
            "line_pattern_hint", getattr(self.instance, "line_pattern_hint", "")
        )

        if document_type == Template.DocumentType.PDF and not pdf_extraction_mode:
            raise serializers.ValidationError(
                {"pdf_extraction_mode": "Requerido cuando document_type='pdf'."}
            )
        if document_type != Template.DocumentType.PDF:
            if pdf_extraction_mode:
                raise serializers.ValidationError(
                    {"pdf_extraction_mode": "Solo aplica cuando document_type='pdf'."}
                )
            if line_pattern_hint:
                raise serializers.ValidationError(
                    {"line_pattern_hint": "Solo aplica cuando document_type='pdf'."}
                )
        return attrs


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

    La validación fuerte de combinaciones extraction_type/scope
    (anchor_text, block_end_anchor, etc.) la resuelve TemplateField.clean(),
    llamado desde la view vía _full_clean.
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
            "scope",
            "anchor_text",
            "anchor_position",
            "block_start_anchor",
            "block_end_anchor",
            "expected_data_type",
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