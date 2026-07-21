# catalogs/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ExcelDeduplicateView, SupplierCatalogRowViewSet

router = DefaultRouter()
router.register(
    "supplier-catalog-rows",
    SupplierCatalogRowViewSet,
    basename="supplier-catalog-row",
)

urlpatterns = router.urls + [
    path(
        "excel/deduplicate/",
        ExcelDeduplicateView.as_view(),
        name="excel-deduplicate",
    ),
]