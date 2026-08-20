from django.contrib import admin
from core.utils.admin import BaseAdmin

from .models import (
    Layout,
    LayoutField,
    NormalizationRule,
)


class LayoutFieldInline(admin.TabularInline):
    model = LayoutField
    extra = 0
    ordering = ("sort_order",)
    fields = (
        "sort_order",
        "name",
    )


@admin.register(Layout)
class LayoutAdmin(BaseAdmin):
    list_display = (
        "code",
        "name",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "code",
        "name",
    )
    ordering = ("code",)
    inlines = (LayoutFieldInline,)


@admin.register(LayoutField)
class LayoutFieldAdmin(BaseAdmin):
    list_display = (
        "layout",
        "name",
        "sort_order",
        "system_field_key",
    )

    search_fields = (
        "name",
        "layout__code",
    )

    list_filter = (
        "system_field_key",
        "layout",
    )

    autocomplete_fields = (
        "layout",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(NormalizationRule)
class NormalizationRuleAdmin(BaseAdmin):
    list_display = (
        "name",
        "rule_type",
        "description",
        "created_at",
    )
    list_filter = (
        "rule_type",
    )
    search_fields = (
        "name",
        "description",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    ordering = ("name",)