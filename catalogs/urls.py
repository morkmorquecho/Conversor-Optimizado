# catalogs/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from catalogs.views import (
    ExcelDeduplicateView,
    SupplierCatalogRowViewSet,
    SupplierCatalogViewSet,
    SupplierViewSet,
)

# /suppliers/
router = DefaultRouter()
router.register("suppliers", SupplierViewSet, basename="supplier")

# /suppliers/{supplier_pk}/catalogs/
catalogs_router = NestedDefaultRouter(router, "suppliers", lookup="supplier")
catalogs_router.register(
    "catalogs", SupplierCatalogViewSet, basename="supplier-catalog"
)

# /suppliers/{supplier_pk}/catalogs/{catalog_pk}/rows/
rows_router = NestedDefaultRouter(catalogs_router, "catalogs", lookup="catalog")
rows_router.register(
    "rows", SupplierCatalogRowViewSet, basename="catalog-row"
)

urlpatterns = (
    router.urls
    + catalogs_router.urls
    + rows_router.urls
    + [
        path(
            "catalogs/deduplicate/",
            ExcelDeduplicateView.as_view(),
            name="excel-deduplicate",
        ),
    ]
)