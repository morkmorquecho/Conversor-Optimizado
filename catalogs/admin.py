from django.contrib import admin

from core.utils.admin import BaseAdmin

from .models import (
    Supplier,
    Currency,
    Umc,
    SupplierCatalog,
    SupplierCatalogColumn,
    SupplierCatalogRow,
)


class SupplierCatalogColumnInline(admin.TabularInline):
    model = SupplierCatalogColumn
    extra = 0
    autocomplete_fields = ("layout_field",)


@admin.register(Supplier)
class SupplierAdmin(BaseAdmin):
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


@admin.register(Currency)
class CurrencyAdmin(BaseAdmin):
    list_display = (
        "code",
        "country",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "code",
        "country",
    )
    ordering = ("code",)


@admin.register(Umc)
class UmcAdmin(BaseAdmin):
    list_display = (
        "code",
        "description",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "code",
        "description",
    )
    ordering = ("code",)


@admin.register(SupplierCatalog)
class SupplierCatalogAdmin(BaseAdmin):
    list_display = (
        "supplier",
        "name",
        "pivot_field_name",
        "is_active",
        "created_at",
    )
    list_filter = (
        "supplier",
        "is_active",
    )
    search_fields = (
        "supplier__code",
        "supplier__name",
        "name",
        "pivot_field_name",
    )
    autocomplete_fields = (
        "supplier",
    )
    ordering = (
        "supplier__code",
        "name",
    )
    inlines = (
        SupplierCatalogColumnInline,
    )


@admin.register(SupplierCatalogColumn)
class SupplierCatalogColumnAdmin(BaseAdmin):
    list_display = (
        "supplier_catalog",
        "source_name",
        "layout_field",
    )
    list_filter = (
        "supplier_catalog__supplier",
    )
    search_fields = (
        "supplier_catalog__name",
        "supplier_catalog__supplier__code",
        "supplier_catalog__supplier__name",
        "source_name",
        "layout_field__name",
    )
    autocomplete_fields = (
        "supplier_catalog",
        "layout_field",
    )
    ordering = (
        "supplier_catalog",
        "source_name",
    )


@admin.register(SupplierCatalogRow)
class SupplierCatalogRowAdmin(BaseAdmin):
    list_display = (
        "supplier_catalog",
        "pivot_value",
        "created_at",
    )
    list_filter = (
        "supplier_catalog__supplier",
    )
    search_fields = (
        "supplier_catalog__name",
        "supplier_catalog__supplier__code",
        "supplier_catalog__supplier__name",
        "pivot_value",
    )
    autocomplete_fields = (
        "supplier_catalog",
    )
    ordering = (
        "supplier_catalog",
        "pivot_value",
    )