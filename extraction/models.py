# extraction/models.py
from django.db import models

from catalogs.models import Supplier
from core.models import BaseModel
from layouts.models import LayoutField
from templates.models import PdfExtractionConfig, Template


class ExtractionJob(BaseModel):
    """Record of every processed invoice and its status."""

    class FileFormat(models.TextChoices):
        XML = "xml", "XML"
        XLSX = "xlsx", "XLSX"
        PDF = "pdf", "PDF"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSED = "processed", "Processed"
        ERROR = "error", "Error"
        REVIEW = "review", "Review"

    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="extraction_jobs"
    )
    source_file = models.CharField(max_length=512)
    file_format = models.CharField(max_length=8, choices=FileFormat.choices)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )

    template = models.ForeignKey(
        Template,
        on_delete=models.PROTECT,
        related_name="extraction_jobs",
        null=True,
        blank=True,
    )
    pdf_extraction_config = models.ForeignKey(
        PdfExtractionConfig,
        on_delete=models.PROTECT,
        related_name="extraction_jobs",
        null=True,
        blank=True,
    )

    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "created_at"])]

    def __str__(self):
        return f"Job #{self.pk} - {self.supplier.code} ({self.status})"


class ExtractionResult(BaseModel):
    """Extracted and normalized value for a layout field within a job."""

    extraction_job = models.ForeignKey(
        ExtractionJob, on_delete=models.CASCADE, related_name="results"
    )
    layout_field = models.ForeignKey(
        LayoutField, on_delete=models.PROTECT, related_name="extraction_results"
    )
    raw_value = models.TextField(blank=True)
    normalized_value = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["extraction_job", "layout_field"],
                name="unique_layout_field_per_job",
            )
        ]
        ordering = ["extraction_job", "layout_field__sort_order"]

    def __str__(self):
        return f"{self.extraction_job} - {self.layout_field.name}"


class ExtractionError(BaseModel):
    """Error details for manual review."""

    extraction_job = models.ForeignKey(
        ExtractionJob, on_delete=models.CASCADE, related_name="errors"
    )
    field_name = models.CharField(
        max_length=255,
        blank=True,
    )
    layout_field = models.ForeignKey(
        LayoutField,
        on_delete=models.SET_NULL,
        related_name="extraction_errors",
        null=True,
        blank=True,
    )
    message = models.TextField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Error on job #{self.extraction_job_id} - {self.field_name or self.layout_field}"