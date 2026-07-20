from rest_framework.routers import DefaultRouter

from .views import SupplierCatalogRowViewSet

router = DefaultRouter()
router.register(
    "supplier-catalog-rows",
    SupplierCatalogRowViewSet,
    basename="supplier-catalog-row",
)

urlpatterns = router.urls