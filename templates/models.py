# templates/models.py
from django.db import models

from catalogs.models import Supplier
from core.models import BaseModel
from layouts.models import LayoutField, NormalizationRule


class Template(BaseModel):
    """Supplier template for XML/XLSX extraction."""

    class DocumentType(models.TextChoices):
        XML = "xml", "XML"
        XLSX = "xlsx", "XLSX"

    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="templates"
    )
    name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=8, choices=DocumentType.choices)
    

    class Meta:
        ordering = ["supplier", "name"]

    def __str__(self):
        return f"{self.supplier.code} - {self.name} ({self.document_type})"


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
        max_length=128, blank=True, 
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["template", "layout_field"],
                name="unique_layout_field_per_template",
            )
        ]
        ordering = ["template", "layout_field__sort_order"]

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
    base_prompt = models.TextField()
    hints = models.TextField(
        blank=True,
    )
    
    class Meta:
        ordering = ["supplier", "-created_at"]

    def __str__(self):
        return f"PDF config - {self.supplier.code}"