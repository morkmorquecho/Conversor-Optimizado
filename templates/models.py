from django.db import models

from catalogs.models import Supplier
from layouts.models import Layout, LayoutField, NormalizationRule

from core.models import BaseModel

class Template(BaseModel):
    """Supplier template for XML/XLSX/PDF extraction, mapping into a target Layout."""

    class DocumentType(models.TextChoices):
        XML = "xml", "XML"
        XLSX = "xlsx", "XLSX"
        PDF = "pdf", "PDF"

    class PdfExtractionMode(models.TextChoices):
        TEXT_ONLY = "text_only", "Solo texto"
        TEXT_AND_TABLES = "text_and_tables", "Texto y tablas"

    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="templates"
    )
    layout = models.ForeignKey(
        Layout, on_delete=models.PROTECT, related_name="templates"
    )
    name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=8, choices=DocumentType.choices)
    pdf_extraction_mode = models.CharField(
        max_length=20,
        choices=PdfExtractionMode.choices,
        blank=True,
        help_text="Solo aplica cuando document_type='pdf'. Define si pdfplumber "
                   "extrae solo texto plano o texto + tablas detectadas.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["supplier", "layout", "document_type"],
                condition=models.Q(is_active=True),
                name="unique_active_template_per_supplier_layout_format",
            )
        ]
        ordering = ["supplier", "layout", "name"]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.document_type == self.DocumentType.PDF and not self.pdf_extraction_mode:
            raise ValidationError(
                "pdf_extraction_mode es requerido cuando document_type='pdf'."
            )
        if self.document_type != self.DocumentType.PDF and self.pdf_extraction_mode:
            raise ValidationError(
                "pdf_extraction_mode solo aplica cuando document_type='pdf'."
            )

    def __str__(self):
        return f"{self.supplier.code} -> {self.layout.code} ({self.document_type})"


class TemplateField(BaseModel):
    """Defines which source field is extracted and mapped to a layout field."""

    class ExtractionType(models.TextChoices):
        HEADER_NAME = "header_name", "Header name"
        XPATH = "xpath", "XPath"
        LLM_TEXT = "llm_text", "LLM (texto libre)"

    class AnchorPosition(models.TextChoices):
        AFTER = "after", "Después del ancla"
        BEFORE = "before", "Antes del ancla"
        SAME_LINE = "same_line", "Misma línea que el ancla"
        BELOW = "below", "Debajo del ancla"

    class ExpectedDataType(models.TextChoices):
        TEXT = "text", "Texto"
        DATE = "date", "Fecha"
        AMOUNT = "amount", "Monto"
        NUMBER = "number", "Número"

    template = models.ForeignKey(
        Template, on_delete=models.CASCADE, related_name="fields"
    )
    layout_field = models.ForeignKey(
        LayoutField, on_delete=models.PROTECT, related_name="template_fields"
    )
    source_field = models.CharField(
        max_length=255,
        blank=True,
        help_text="Requerido para header_name (nombre de columna) y xpath. "
                   "No aplica para llm_text (usa anchor_text en su lugar).",
    )
    extraction_type = models.CharField(
        max_length=16, choices=ExtractionType.choices
    )
    worksheet = models.CharField(
        max_length=128, blank=True, help_text="XLSX only"
    )
    header_occurrence = models.PositiveIntegerField(
        default=1,
        help_text="Si el encabezado se repite en el excel, indica qué ocurrencia "
                "corresponde a este campo (1 = primera columna con ese nombre, "
                "2 = segunda, etc.). Para encabezados únicos, deja 1.",
    )
    anchor_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="LLM only. Texto literal presente en el documento que sirve de "
                   "referencia para ubicar el valor (ej. 'Fecha de factura:').",
    )
    anchor_position = models.CharField(
        max_length=16,
        choices=AnchorPosition.choices,
        blank=True,
        help_text="LLM only. Posición del valor respecto a anchor_text.",
    )
    expected_data_type = models.CharField(
        max_length=16,
        choices=ExpectedDataType.choices,
        blank=True,
        help_text="LLM only. Hint del tipo de valor esperado (no convierte, "
                   "solo guía al LLM)",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["template", "layout_field"],
                name="unique_layout_field_per_template",
            ),
            models.UniqueConstraint(
                fields=["template", "source_field", "header_occurrence"],
                condition=models.Q(extraction_type="header_name"),
                name="unique_source_field_occurrence_per_template",
            ),
            models.UniqueConstraint(
                fields=["template", "source_field"],
                condition=models.Q(extraction_type="xpath"),
                name="unique_xpath_per_template",
            ),
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

        if self.extraction_type in (
            self.ExtractionType.HEADER_NAME,
            self.ExtractionType.XPATH,
        ):
            if not self.source_field:
                raise ValidationError(
                    "source_field es requerido para header_name y xpath."
                )
            if self.anchor_text or self.anchor_position:
                raise ValidationError(
                    "anchor_text/anchor_position solo aplican a extraction_type='llm_text'."
                )

        if self.extraction_type == self.ExtractionType.LLM_TEXT:
            if self.source_field:
                raise ValidationError(
                    "source_field no aplica para llm_text; usa anchor_text."
                )
            if not self.anchor_text or not self.anchor_position:
                raise ValidationError(
                    "anchor_text y anchor_position son requeridos para llm_text."
                )
            if self.worksheet:
                raise ValidationError(
                    "worksheet no aplica para llm_text (es exclusivo de XLSX)."
                )

    def __str__(self):
        if self.extraction_type == self.ExtractionType.LLM_TEXT:
            return f"{self.template} -> {self.layout_field.name} (ancla: {self.anchor_text})"
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
            ),
        ]
        ordering = ["template_field", "sort_order"]

    def __str__(self):
        return f"{self.template_field} - {self.normalization_rule.name} (#{self.sort_order})"

