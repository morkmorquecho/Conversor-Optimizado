from django.contrib import admin

from core.utils.admin import BaseAdmin

from .models import (
    ExtractionBatch,
    ExtractionJob,
    ExtractionResult,
    ExtractionError,
)


class ExtractionResultInline(admin.TabularInline):
    model = ExtractionResult
    extra = 0
    autocomplete_fields = ("layout_field",)
    readonly_fields = ("created_at", "updated_at")


class ExtractionErrorInline(admin.TabularInline):
    model = ExtractionError
    extra = 0
    autocomplete_fields = ("layout_field",)
    readonly_fields = ("created_at", "updated_at")


class ExtractionJobInline(admin.TabularInline):
    model = ExtractionJob
    extra = 0
    autocomplete_fields = ("extraction_batch",)
    readonly_fields = (
        "row_number",
        "status",
        "created_at",
        "updated_at",
    )
    fields = (
        "row_number",
        "status",
        "created_at",
        "updated_at",
    )
    ordering = ("row_number",)


@admin.register(ExtractionBatch)
class ExtractionBatchAdmin(BaseAdmin):
    list_display = (
        "id",
        "source_file",
        "supplier",
        "file_format",
        "status",
        "template",
        "total_records",
        "successful_records",
        "failed_records",
        "created_at",
    )

    list_filter = (
        "status",
        "file_format",
        "supplier",
        "template",
    )

    search_fields = (
        "id",
        "source_file",
        "supplier__code",
        "supplier__name",
        "template__name",
    )

    autocomplete_fields = (
        "supplier",
        "template",
        "supplier_catalog",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    list_per_page = 100

    inlines = (
        ExtractionJobInline,
    )


@admin.register(ExtractionJob)
class ExtractionJobAdmin(BaseAdmin):
    list_display = (
        "id",
        "extraction_batch",
        "row_number",
        "get_supplier",
        "get_file_format",
        "get_template",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "extraction_batch__file_format",
        "extraction_batch__supplier",
    )

    search_fields = (
        "id",
        "extraction_batch__id",
        "extraction_batch__source_file",
        "extraction_batch__supplier__code",
        "extraction_batch__supplier__name",
        "extraction_batch__template__name",
    )

    autocomplete_fields = (
        "extraction_batch",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 100

    inlines = (
        ExtractionResultInline,
        ExtractionErrorInline,
    )

    @admin.display(
        description="Supplier",
        ordering="extraction_batch__supplier",
    )
    def get_supplier(self, obj):
        return obj.extraction_batch.supplier

    @admin.display(
        description="File format",
        ordering="extraction_batch__file_format",
    )
    def get_file_format(self, obj):
        return obj.extraction_batch.file_format

    @admin.display(
        description="Template",
        ordering="extraction_batch__template",
    )
    def get_template(self, obj):
        return obj.extraction_batch.template


@admin.register(ExtractionResult)
class ExtractionResultAdmin(BaseAdmin):
    list_display = (
        "id",
        "extraction_job",
        "layout_field",
        "normalized_value",
        "created_at",
    )

    list_filter = (
        "layout_field",
    )

    search_fields = (
        "extraction_job__id",
        "extraction_job__extraction_batch__id",
        "extraction_job__extraction_batch__source_file",
        "layout_field__name",
        "raw_value",
        "normalized_value",
    )

    autocomplete_fields = (
        "extraction_job",
        "layout_field",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "extraction_job",
        "layout_field",
    )


@admin.register(ExtractionError)
class ExtractionErrorAdmin(BaseAdmin):
    list_display = (
        "id",
        "extraction_job",
        "field_name",
        "layout_field",
        "created_at",
    )

    list_filter = (
        "layout_field",
    )

    search_fields = (
        "extraction_job__id",
        "extraction_job__extraction_batch__id",
        "extraction_job__extraction_batch__source_file",
        "field_name",
        "message",
        "layout_field__name",
    )

    autocomplete_fields = (
        "extraction_job",
        "layout_field",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )