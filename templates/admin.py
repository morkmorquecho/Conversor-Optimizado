from django.contrib import admin
from core.utils.admin import BaseAdmin

from .models import (
    Template,
    TemplateField,
    TemplateFieldRule,
    PdfExtractionConfig,
)


class TemplateFieldInline(admin.TabularInline):
    model = TemplateField
    extra = 0
    autocomplete_fields = ("layout_field",)
    fields = (
        "layout_field",
        "source_field",
        "extraction_type",
        "worksheet",
    )


@admin.register(Template)
class TemplateAdmin(BaseAdmin):
    list_display = (
        "name",
        "supplier",
        "layout",
        "document_type",
        "is_active",
        "created_at",
    )
    list_filter = (
        "supplier",
        "layout",
        "document_type",
        "is_active",
    )
    search_fields = (
        "name",
        "supplier__code",
        "supplier__name",
        "layout__code",
        "layout__name",
    )
    autocomplete_fields = (
        "supplier",
        "layout",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    ordering = (
        "supplier__code",
        "layout__code",
        "name",
    )
    list_per_page = 100
    inlines = (TemplateFieldInline,)


class TemplateFieldRuleInline(admin.TabularInline):
    model = TemplateFieldRule
    extra = 0
    autocomplete_fields = ("normalization_rule",)
    fields = (
        "sort_order",
        "normalization_rule",
    )
    ordering = ("sort_order",)


@admin.register(TemplateField)
class TemplateFieldAdmin(BaseAdmin):
    list_display = (
        "template",
        "layout_field",
        "source_field",
        "extraction_type",
        "worksheet",
    )
    list_filter = (
        "extraction_type",
        "template__supplier",
    )
    search_fields = (
        "source_field",
        "layout_field__name",
        "template__name",
        "template__supplier__code",
    )
    autocomplete_fields = (
        "template",
        "layout_field",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    ordering = (
        "template",
        "layout_field__sort_order",
    )
    inlines = (TemplateFieldRuleInline,)


@admin.register(TemplateFieldRule)
class TemplateFieldRuleAdmin(BaseAdmin):
    list_display = (
        "template_field",
        "normalization_rule",
        "sort_order",
    )
    list_filter = (
        "normalization_rule__rule_type",
    )
    search_fields = (
        "template_field__template__name",
        "template_field__layout_field__name",
        "normalization_rule__name",
    )
    autocomplete_fields = (
        "template_field",
        "normalization_rule",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    ordering = (
        "template_field",
        "sort_order",
    )


@admin.register(PdfExtractionConfig)
class PdfExtractionConfigAdmin(BaseAdmin):
    list_display = (
        "supplier",
        "layout",
        "is_active",
        "created_at",
    )
    list_filter = (
        "supplier",
        "layout",
        "is_active",
    )
    search_fields = (
        "supplier__code",
        "supplier__name",
        "layout__code",
        "layout__name",
    )
    autocomplete_fields = (
        "supplier",
        "layout",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    ordering = (
        "supplier__code",
        "-created_at",
    )
    list_per_page = 100