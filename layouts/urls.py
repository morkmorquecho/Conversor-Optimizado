# layouts/urls.py
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import LayoutFieldViewSet, LayoutViewSet, NormalizationRuleViewSet

router = DefaultRouter()
router.register("layouts", LayoutViewSet, basename="layout")
router.register(
    "normalization-rules", NormalizationRuleViewSet, basename="normalization-rule"
)

layout_router = NestedDefaultRouter(router, "layouts", lookup="layout")
layout_router.register("fields", LayoutFieldViewSet, basename="layout-field")

urlpatterns = router.urls + layout_router.urls