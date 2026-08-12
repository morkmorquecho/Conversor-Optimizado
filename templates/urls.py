# templates/urls.py
from rest_framework_nested.routers import NestedDefaultRouter

# Se reutiliza el router base ya definido en catalogs/urls.py (el que
# registra "suppliers") para anidar templates bajo
# suppliers/{supplier_pk}/templates/, en vez de volver a registrar
# SupplierViewSet acá. OJO: se anida contra `router`, no contra
# `supplier_router` — este último ya está anidado para "catalogs" y no
# sirve como padre de un recurso hermano como "templates".
from catalogs.urls import router

from .views import TemplateFieldRuleViewSet, TemplateFieldViewSet, TemplateViewSet

template_router = NestedDefaultRouter(router, "suppliers", lookup="supplier")
template_router.register("templates", TemplateViewSet, basename="template")

template_field_router = NestedDefaultRouter(
    template_router, "templates", lookup="template"
)
template_field_router.register(
    "fields", TemplateFieldViewSet, basename="template-field"
)

template_field_rule_router = NestedDefaultRouter(
    template_field_router, "fields", lookup="field"
)
template_field_rule_router.register(
    "rules", TemplateFieldRuleViewSet, basename="template-field-rule"
)

urlpatterns = (
    template_router.urls
    + template_field_router.urls
    + template_field_rule_router.urls
)