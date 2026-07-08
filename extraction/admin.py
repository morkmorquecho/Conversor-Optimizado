from django.contrib import admin
from core.utils.admin import BaseAdmin

from .models import (
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


@admin.register(ExtractionJob)
class ExtractionJobAdmin(BaseAdmin):
    list_display = (
        "id",
        "supplier",
        "file_format",
        "status",
        "template",
        "processed_at",
        "created_at",
    )
    list_filter = (
        "status",
        "file_format",
        "supplier",
    )
    search_fields = (
        "id",
        "supplier__code",
        "supplier__name",
        "source_file",
        "template__name",
    )
    autocomplete_fields = (
        "supplier",
        "template",
        "pdf_extraction_config",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "processed_at",
    )
    ordering = ("-created_at",)
    list_per_page = 100

    inlines = (
        ExtractionResultInline,
        ExtractionErrorInline,
    )


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
    ordering = ("extraction_job", "layout_field")


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
    ordering = ("-created_at",)