from django.db import models

from core.models import BaseModel

#Se registran los campos que se utilizaran en el layout final en este caso los usados en casa rojo y azul
class LayoutField(BaseModel):
    """Destination field in the final layout (supplier_code, invoice_date, etc.)."""

    name = models.CharField(max_length=64, unique=True)
    sort_order = models.PositiveIntegerField(
    )

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.name


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