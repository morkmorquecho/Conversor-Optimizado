from django.contrib import admin

from core.utils.admin import BaseAdmin

from .models import (
    Template,
    TemplateField,
    TemplateFieldRule,
)


class TemplateFieldInline(admin.TabularInline):
    model = TemplateField
    extra = 0
    fields = (
        "layout_field",
        "extraction_type",
        "source_field",
        "worksheet",
        "header_occurrence",
        "scope",
        "anchor_text",
        "anchor_position",
        "block_start_anchor",
        "block_end_anchor",
        "expected_data_type",
    )


@admin.register(Template)
class TemplateAdmin(BaseAdmin):
    list_display = (
        "name",
        "supplier",
        "layout",
        "document_type",
        "pdf_extraction_mode",
    )
    list_filter = (
        "document_type",
        "pdf_extraction_mode",
        "supplier",
        "layout",
    )
    search_fields = (
        "name",
        "supplier__name",
        "supplier__code",
        "layout__name",
        "layout__code",
    )
    list_select_related = (
        "supplier",
        "layout",
    )
    inlines = (TemplateFieldInline,)


@admin.register(TemplateField)
class TemplateFieldAdmin(BaseAdmin):
    list_display = (
        "layout_field",
        "template",
        "extraction_type",
        "scope",
        "source_field",
        "expected_data_type",
    )
    list_filter = (
        "extraction_type",
        "scope",
        "expected_data_type",
        "template__document_type",
    )
    search_fields = (
        "source_field",
        "anchor_text",
        "block_start_anchor",
        "block_end_anchor",
        "template__name",
        "layout_field__name",
    )
    list_select_related = (
        "template",
        "layout_field",
    )


@admin.register(TemplateFieldRule)
class TemplateFieldRuleAdmin(BaseAdmin):
    list_display = (
        "template_field",
        "normalization_rule",
        "sort_order",
    )
    list_filter = (
        "normalization_rule",
        "template_field__template",
    )
    search_fields = (
        "template_field__source_field",
        "template_field__anchor_text",
        "template_field__template__name",
        "normalization_rule__name",
    )
    list_select_related = (
        "template_field",
        "normalization_rule",
    )