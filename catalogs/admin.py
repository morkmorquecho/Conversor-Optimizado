from django.contrib import admin
from core.utils.admin import BaseAdmin

from .models import (
    Supplier,
    Currency,
    Umc,
    SupplierCatalogItem,
)


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


@admin.register(SupplierCatalogItem)
class SupplierCatalogItemAdmin(BaseAdmin):
    list_display = (
        "supplier",
        "tariff_code",
        "commercial_description",
        "created_at",
    )
    list_filter = (
        "supplier",
    )
    search_fields = (
        "supplier__code",
        "supplier__name",
        "tariff_code",
        "commercial_description",
    )
    autocomplete_fields = (
        "supplier",
    )
    ordering = (
        "supplier__code",
        "tariff_code",
    )