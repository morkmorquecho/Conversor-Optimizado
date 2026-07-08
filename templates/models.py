from django.db import models

from catalogs.models import Supplier
from layouts.models import Layout, LayoutField, NormalizationRule

from core.models import BaseModel

class Template(BaseModel):
    """Supplier template for XML/XLSX extraction, mapping into a target Layout."""

    class DocumentType(models.TextChoices):
        XML = "xml", "XML"
        XLSX = "xlsx", "XLSX"

    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="templates"
    )
    layout = models.ForeignKey(
        Layout, on_delete=models.PROTECT, related_name="templates"
    )
    name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=8, choices=DocumentType.choices)


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["supplier", "layout", "document_type"],
                condition=models.Q(is_active=True),
                name="unique_active_template_per_supplier_layout_format",
            )
        ]
        ordering = ["supplier", "layout", "name"]

    def __str__(self):
        return f"{self.supplier.code} -> {self.layout.code} ({self.document_type})"


class TemplateField(BaseModel):
    """Defines which source field is extracted and mapped to a layout field."""

    class ExtractionType(models.TextChoices):
        HEADER_NAME = "header_name", "Header name"
        XPATH = "xpath", "XPath"

    template = models.ForeignKey(
        Template, on_delete=models.CASCADE, related_name="fields"
    )
    layout_field = models.ForeignKey(
        LayoutField, on_delete=models.PROTECT, related_name="template_fields"
    )
    source_field = models.CharField(
        max_length=255, 
    )
    extraction_type = models.CharField(
        max_length=16, choices=ExtractionType.choices
    )
    worksheet = models.CharField(
        max_length=128, blank=True, help_text="XLSX only"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["template", "layout_field"],
                name="unique_layout_field_per_template",
            )
        ]
        ordering = ["template", "layout_field__sort_order"]

    def clean(self):
        from django.core.exceptions import ValidationError

        if (
            self.template_id
            and self.layout_field_id
            and self.layout_field.layout_id != self.template.layout_id
        ):
            raise ValidationError(
                "layout_field must belong to the same layout as the template."
            )

    def __str__(self):
        return f"{self.template} -> {self.layout_field.name}"


class TemplateFieldRule(BaseModel):
    """Chains normalization rules onto a template field, in execution order."""

    template_field = models.ForeignKey(
        TemplateField, on_delete=models.CASCADE, related_name="rules"
    )
    normalization_rule = models.ForeignKey(
        NormalizationRule, on_delete=models.PROTECT, related_name="template_fields"
    )
    sort_order = models.PositiveIntegerField(
        help_text="Execution order when multiple rules are chained"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["template_field", "normalization_rule"],
                name="unique_rule_per_template_field",
            )
        ]
        ordering = ["template_field", "sort_order"]

    def __str__(self):
        return f"{self.template_field} - {self.normalization_rule.name} (#{self.sort_order})"


class PdfExtractionConfig(BaseModel):
    """LLM prompt configuration for text-extractable PDFs."""

    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="pdf_extraction_configs"
    )
    layout = models.ForeignKey(
        Layout, on_delete=models.PROTECT, related_name="pdf_extraction_configs"
    )
    base_prompt = models.TextField()
    hints = models.TextField(
        blank=True,
        help_text="Supplier-specific instructions such as currency, field locations, etc.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["supplier", "-created_at"]

    def __str__(self):
        return f"PDF config - {self.supplier.code}"