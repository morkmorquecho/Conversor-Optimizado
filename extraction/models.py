# extraction/models.py
from django.db import models

from catalogs.models import Supplier, SupplierCatalog
from core.models import BaseModel
from layouts.models import LayoutField
from templates.models import PdfExtractionConfig, Template

class ExtractionBatch(BaseModel):
    """
    Represents one complete extraction process from an uploaded file.

    One batch can contain multiple ExtractionJobs.
    For example, an Excel file with 500 rows creates:
        1 ExtractionBatch
        500 ExtractionJobs
    """

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
        Supplier,
        on_delete=models.PROTECT,
        related_name="extraction_batches",
    )
    source_file = models.CharField(max_length=512)
    file_format = models.CharField(
        max_length=8,
        choices=FileFormat.choices,
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    template = models.ForeignKey(
        Template,
        on_delete=models.PROTECT,
        related_name="extraction_batches",
        null=True,
        blank=True,
    )
    pdf_extraction_config = models.ForeignKey(
        PdfExtractionConfig,
        on_delete=models.PROTECT,
        related_name="extraction_batches",
        null=True,
        blank=True,
    )
    supplier_catalog = models.ForeignKey(
        SupplierCatalog,
        on_delete=models.PROTECT,
        related_name="extraction_batches",
        null=True,
        blank=True,
    )
    total_records = models.PositiveIntegerField(default=0)
    successful_records = models.PositiveIntegerField(default=0)
    failed_records = models.PositiveIntegerField(default=0)
    processed_at = models.DateTimeField(null=True, blank=True)    
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["status", "created_at"]
            ),
        ]

    def __str__(self):
        return (
            f"Batch #{self.pk} - "
            f"{self.source_file} "
            f"({self.status})"
        )
    
class ExtractionJob(BaseModel):
    """
    Represents one individual record processed within an extraction batch.

    Example:

        ExtractionBatch
            ├── ExtractionJob (row 1)
            ├── ExtractionJob (row 2)
            └── ExtractionJob (row 3)
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSED = "processed", "Processed"
        ERROR = "error", "Error"
        REVIEW = "review", "Review"

    extraction_batch = models.ForeignKey(
        ExtractionBatch,
        on_delete=models.CASCADE,
        related_name="jobs",
    )

    row_number = models.PositiveIntegerField()

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ["row_number"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "extraction_batch",
                    "row_number",
                ],
                name="unique_row_per_extraction_batch",
            )
        ]

    def __str__(self):
        return (
            f"Job #{self.pk} - "
            f"Batch #{self.extraction_batch_id} - "
            f"Row {self.row_number}"
        )

class ExtractionResult(BaseModel):
    """
    Extracted and normalized value for a layout field
    within an individual extraction job.
    """

    extraction_job = models.ForeignKey(
        ExtractionJob,
        on_delete=models.CASCADE,
        related_name="results",
    )

    layout_field = models.ForeignKey(
        LayoutField,
        on_delete=models.PROTECT,
        related_name="extraction_results",
    )

    raw_value = models.TextField(blank=True)

    normalized_value = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "extraction_job",
                    "layout_field",
                ],
                name="unique_layout_field_per_job",
            )
        ]

        ordering = [
            "extraction_job",
            "layout_field__sort_order",
        ]

    def __str__(self):
        return (
            f"{self.extraction_job} - "
            f"{self.layout_field.name}"
        )

class ExtractionError(BaseModel):
    """
    Error associated with an individual extraction job.
    """

    extraction_job = models.ForeignKey(
        ExtractionJob,
        on_delete=models.CASCADE,
        related_name="errors",
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
        return (
            f"Error on job #{self.extraction_job_id} - "
            f"{self.field_name or self.layout_field}"
        )
    