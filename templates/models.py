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

    # --- PDF only ---
    pdf_extraction_mode = models.CharField(
        max_length=20,
        choices=PdfExtractionMode.choices,
        blank=True,
        help_text="Solo aplica cuando document_type='pdf'. Define si pdfplumber "
                   "extrae solo texto plano o texto + tablas detectadas. "
                   "Obligatorio 'text_and_tables' si el template tiene campos "
                   "scope='line_item'.",
    )
    line_pattern_hint = models.TextField(
        blank=True,
        help_text="PDF only. Descripción del patrón posicional de una línea de "
                   "renglón cuando NO hay tabla detectada ni encabezado de "
                   "columna identificable en el texto. Ej: 'Cada línea trae "
                   "cantidad, precio y descripción, en ese orden, separados "
                   "por espacios. Ejemplo: 4  10.00  Manzanas'. Solo tiene "
                   "sentido si existe al menos un TemplateField con "
                   "scope='line_item'.",
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
        if self.document_type != self.DocumentType.PDF:
            if self.pdf_extraction_mode:
                raise ValidationError(
                    "pdf_extraction_mode solo aplica cuando document_type='pdf'."
                )
            if self.line_pattern_hint:
                raise ValidationError(
                    "line_pattern_hint solo aplica cuando document_type='pdf'."
                )

        # Si hay campos line_item, forzamos text_and_tables (mejor esfuerzo:
        # si pdfplumber no detecta tabla real, el pipeline degrada a texto
        # usando block_start_anchor/block_end_anchor/line_pattern_hint).
        if self.pk and self.document_type == self.DocumentType.PDF:
            has_line_items = self.fields.filter(
                scope=TemplateField.Scope.LINE_ITEM
            ).exists()
            if has_line_items and self.pdf_extraction_mode != self.PdfExtractionMode.TEXT_AND_TABLES:
                raise ValidationError(
                    "pdf_extraction_mode debe ser 'text_and_tables' cuando el "
                    "template tiene campos con scope='line_item'."
                )

    def __str__(self):
        return f"{self.supplier.code} -> {self.layout.code} ({self.document_type})"


class TemplateField(BaseModel):
    """Defines which source field is extracted and mapped to a layout field."""

    class ExtractionType(models.TextChoices):
        HEADER_NAME = "header_name", "Header name"
        XPATH = "xpath", "XPath"
        LLM_TEXT = "llm_text", "LLM (texto libre)"

    class Scope(models.TextChoices):
        HEADER = "header", "Encabezado (valor único por documento)"
        LINE_ITEM = "line_item", "Renglón de partida (se repite por fila)"

    class AnchorPosition(models.TextChoices):
        AFTER = "after", "Después del ancla"
        BEFORE = "before", "Antes del ancla"
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
                   "No aplica para llm_text.",
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

    # --- LLM (PDF) only ---
    scope = models.CharField(
        max_length=10,
        choices=Scope.choices,
        default=Scope.HEADER,
        help_text="LLM only. 'header' = valor único en el documento. "
                   "'line_item' = se repite una vez por cada renglón de una "
                   "tabla de partidas.",
    )

    # -- usado cuando scope='header' --
    anchor_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="LLM + scope='header'. Texto literal presente en el "
                   "documento que sirve de referencia para ubicar el valor "
                   "(ej. 'Fecha de factura:').",
    )
    anchor_position = models.CharField(
        max_length=16,
        choices=AnchorPosition.choices,
        blank=True,
        help_text="LLM + scope='header'. Posición del valor respecto a "
                   "anchor_text.",
    )

    # -- usado cuando scope='line_item' --
    block_start_anchor = models.CharField(
        max_length=255,
        blank=True,
        help_text="LLM + scope='line_item'. Texto que marca el inicio de la "
                   "zona de renglones (ej. encabezado de columna 'Cantidad "
                   "Precio Descripción', si existe). Opcional: si no hay "
                   "texto estable de inicio, se puede dejar vacío y usar "
                   "solo block_end_anchor.",
    )
    block_end_anchor = models.CharField(
        max_length=255,
        blank=True,
        help_text="LLM + scope='line_item'. Texto que marca el fin de la zona "
                   "de renglones (ej. 'Subtotal'). Si se deja vacío, el "
                   "pipeline usa una lista genérica de palabras de corte "
                   "definida a nivel de sistema (Subtotal, Total, IVA, etc.).",
    )

    expected_data_type = models.CharField(
        max_length=16,
        choices=ExpectedDataType.choices,
        blank=True,
        help_text="LLM only. Hint del tipo de valor esperado (no convierte, "
                   "solo guía al LLM; la conversión real la hace "
                   "NormalizationRule).",
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

        errors = []

        if (
            self.template_id
            and self.layout_field_id
            and self.layout_field.layout_id != self.template.layout_id
        ):
            errors.append(
                "layout_field must belong to the same layout as the template."
            )

        is_llm = self.extraction_type == self.ExtractionType.LLM_TEXT

        # --- extraction_type: header_name / xpath ---
        if not is_llm:
            if not self.source_field:
                errors.append(
                    "source_field es requerido para header_name y xpath."
                )
            llm_only_fields = (
                self.anchor_text, self.anchor_position,
                self.block_start_anchor, self.block_end_anchor,
                self.expected_data_type,
            )
            if any(llm_only_fields):
                errors.append(
                    "anchor_text/anchor_position/block_start_anchor/"
                    "block_end_anchor/expected_data_type solo aplican a "
                    "extraction_type='llm_text'."
                )
            if self.scope != self.Scope.HEADER:
                errors.append(
                    "scope solo aplica a extraction_type='llm_text'."
                )

        # --- extraction_type: llm_text ---
        if is_llm:
            if self.source_field:
                errors.append(
                    "source_field no aplica para llm_text; usa anchor_text "
                    "(scope='header') o block_start_anchor/block_end_anchor "
                    "(scope='line_item')."
                )
            if self.worksheet:
                errors.append(
                    "worksheet no aplica para llm_text (es exclusivo de XLSX)."
                )

            if self.scope == self.Scope.HEADER:
                if not self.anchor_text or not self.anchor_position:
                    errors.append(
                        "anchor_text y anchor_position son requeridos cuando "
                        "scope='header' y extraction_type='llm_text'."
                    )
                if self.block_start_anchor or self.block_end_anchor:
                    errors.append(
                        "block_start_anchor/block_end_anchor solo aplican a "
                        "scope='line_item'."
                    )

            if self.scope == self.Scope.LINE_ITEM:
                if self.anchor_text or self.anchor_position:
                    errors.append(
                        "anchor_text/anchor_position solo aplican a "
                        "scope='header'. Para 'line_item' usa "
                        "block_start_anchor/block_end_anchor."
                    )
                if not self.block_end_anchor:
                    errors.append(
                        "block_end_anchor es requerido para scope='line_item' "
                        "(si el proveedor no tiene un texto propio de cierre, "
                        "usa una de las palabras de corte genéricas del "
                        "sistema, ej. 'Subtotal')."
                    )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        if self.extraction_type == self.ExtractionType.LLM_TEXT:
            if self.scope == self.Scope.LINE_ITEM:
                return (
                    f"{self.template} -> {self.layout_field.name} "
                    f"(line_item, hasta: {self.block_end_anchor})"
                )
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