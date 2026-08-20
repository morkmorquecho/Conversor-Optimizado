from django.contrib import admin

from core.mixins import SoftDeleteAdminMixin
from core.utils.admin import BaseAdmin

from .models import (
    Supplier,
    Currency,
    SupplierCatalogPivotMapping,
    Umc,
    SupplierCatalog,
    SupplierCatalogColumn,
    SupplierCatalogRow,
    SupplierCatalogColumnLayoutField,
)


# -------------------------
# SupplierCatalogColumnLayoutField
# -------------------------

class SupplierCatalogColumnLayoutFieldInline(admin.TabularInline):
    model = SupplierCatalogColumnLayoutField
    extra = 1
    autocomplete_fields = (
        "layout_field",
    )


@admin.register(SupplierCatalogColumnLayoutField)
class SupplierCatalogColumnLayoutFieldAdmin(BaseAdmin, SoftDeleteAdminMixin):
    list_display = (
        "column",
        "layout_field",
    )

    search_fields = (
        "column__source_name",
        "column__supplier_catalog__name",
        "layout_field__name",
    )

    autocomplete_fields = (
        "column",
        "layout_field",
    )

    list_filter = (
        "layout_field__layout",
    )


# -------------------------
# Supplier
# -------------------------

@admin.register(Supplier)
class SupplierAdmin(BaseAdmin, SoftDeleteAdminMixin):
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

    ordering = (
        "code",
    )


# -------------------------
# Currency
# -------------------------

@admin.register(Currency)
class CurrencyAdmin(BaseAdmin, SoftDeleteAdminMixin):
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

    ordering = (
        "code",
    )


# -------------------------
# UMC
# -------------------------

@admin.register(Umc)
class UmcAdmin(BaseAdmin, SoftDeleteAdminMixin):
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

    ordering = (
        "code",
    )


# -------------------------
# SupplierCatalogColumn
# -------------------------

class SupplierCatalogColumnInline(admin.TabularInline):
    model = SupplierCatalogColumn
    extra = 1

    fields = (
        "source_name",
    )


@admin.register(SupplierCatalogColumn)
class SupplierCatalogColumnAdmin(BaseAdmin, SoftDeleteAdminMixin):
    list_display = (
        "supplier_catalog",
        "source_name",
    )

    list_filter = (
        "supplier_catalog__supplier",
    )

    search_fields = (
        "source_name",
        "supplier_catalog__name",
        "supplier_catalog__supplier__code",
        "supplier_catalog__supplier__name",
    )

    autocomplete_fields = (
        "supplier_catalog",
    )

    ordering = (
        "supplier_catalog",
        "source_name",
    )
# -------------------------
# SupplierCatalog
# -------------------------

@admin.register(SupplierCatalog)
class SupplierCatalogAdmin(BaseAdmin, SoftDeleteAdminMixin):
    list_display = (
        "supplier",
        "name",
        "pivot_field_name",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "supplier",
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


# -------------------------
# SupplierCatalogRow
# -------------------------

@admin.register(SupplierCatalogRow)
class SupplierCatalogRowAdmin(BaseAdmin, SoftDeleteAdminMixin):
    list_display = (
        "supplier_catalog",
        "pivot_value",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "supplier_catalog__supplier",
    )

    search_fields = (
        "pivot_value",
        "supplier_catalog__name",
        "supplier_catalog__supplier__code",
        "supplier_catalog__supplier__name",
    )

    autocomplete_fields = (
        "supplier_catalog",
    )

    ordering = (
        "supplier_catalog",
        "pivot_value",
    )


@admin.register(SupplierCatalogPivotMapping)
class SupplierCatalogPivotMappingAdmin(BaseAdmin):
    list_display = (
        "template",
        "supplier_catalog",
        "pivot_template_field",
    )

    list_filter = (
        "template",
        "supplier_catalog",
    )

    search_fields = (
        "template__name",
        "supplier_catalog__name",
        "pivot_template_field__name",
    )

    autocomplete_fields = (
        "template",
        "supplier_catalog",
        "pivot_template_field",
    )