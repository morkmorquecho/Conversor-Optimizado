from django.db import models
from django.db.models.constraints import Deferrable
from core.models import BaseModel


class Layout(BaseModel):
    """A target output layout (e.g. Casa Azul, Casa Roja)."""

    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)


    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.name


class LayoutField(BaseModel):
    """Destination field within a specific layout (supplier_code, invoice_date, etc.)."""

    class SystemFieldKey(models.TextChoices):
        NONE = "", "No es campo de sistema"
        SUPPLIER_CODE = "supplier_code", "Código del proveedor"

    layout = models.ForeignKey(
        Layout, on_delete=models.CASCADE, related_name="fields"
    )
    name = models.CharField(max_length=64)
    sort_order = models.PositiveIntegerField()
    system_field_key = models.CharField(          # ← campo nuevo
        max_length=64,
        choices=SystemFieldKey.choices,
        blank=True,
        default="",
        help_text="Si se define, este campo se resuelve automáticamente por el "
                  "sistema en vez de mapearse desde un TemplateField.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["layout", "name"], name="unique_field_name_per_layout"
            ),
            models.UniqueConstraint(
                fields=["layout", "sort_order"],
                name="unique_sort_order_per_layout",
                deferrable=Deferrable.DEFERRED,
            ),
        ]
        ordering = ["layout", "sort_order"]

    def __str__(self):
        return f"{self.layout.code} - {self.name}"


class NormalizationRule(BaseModel):
    class RuleType(models.TextChoices):
        DATE_FORMAT = "date_format", "Date format"
        VALUE_MAP = "value_map", "Value map"
        REGEX_REPLACE = "regex_replace", "Regex replace"
        TRIM = "trim", "Trim"
        UPPERCASE = "uppercase", "Uppercase"

    name = models.CharField(
        max_length=128,
        unique=True,
    )
    description = models.CharField(max_length=255, blank=True)
    rule_type = models.CharField(max_length=32, choices=RuleType.choices)
    config = models.JSONField(
        blank=True,
        default=dict,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name