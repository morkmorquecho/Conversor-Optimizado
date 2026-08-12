# templates/views.py
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from core.api_response.error_codes import ErrorCodes
from core.docs.schema_utils import auto_schema_view
from core.mixins import IntPkLookupMixin, ViewSetSentryMixin

from .docs.schemas import (
    TEMPLATE_CREATE_SCHEMA,
    TEMPLATE_DESTROY_SCHEMA,
    TEMPLATE_FIELD_CREATE_SCHEMA,
    TEMPLATE_FIELD_DESTROY_SCHEMA,
    TEMPLATE_FIELD_LIST_SCHEMA,
    TEMPLATE_FIELD_PARTIAL_UPDATE_SCHEMA,
    TEMPLATE_FIELD_RETRIEVE_SCHEMA,
    TEMPLATE_FIELD_RULE_CREATE_SCHEMA,
    TEMPLATE_FIELD_RULE_DESTROY_SCHEMA,
    TEMPLATE_FIELD_RULE_LIST_SCHEMA,
    TEMPLATE_FIELD_RULE_PARTIAL_UPDATE_SCHEMA,
    TEMPLATE_FIELD_RULE_REORDER_SCHEMA,
    TEMPLATE_FIELD_RULE_RETRIEVE_SCHEMA,
    TEMPLATE_FIELD_RULE_UPDATE_SCHEMA,
    TEMPLATE_FIELD_UPDATE_SCHEMA,
    TEMPLATE_LIST_SCHEMA,
    TEMPLATE_PARTIAL_UPDATE_SCHEMA,
    TEMPLATE_RETRIEVE_SCHEMA,
    TEMPLATE_UPDATE_SCHEMA,
)
from .models import Template, TemplateField, TemplateFieldRule
from .serializers import (
    TemplateFieldRuleSerializer,
    TemplateFieldSerializer,
    TemplateSerializer,
)


@auto_schema_view(
    list=TEMPLATE_LIST_SCHEMA,
    create=TEMPLATE_CREATE_SCHEMA,
    retrieve=TEMPLATE_RETRIEVE_SCHEMA,
    update=TEMPLATE_UPDATE_SCHEMA,
    partial_update=TEMPLATE_PARTIAL_UPDATE_SCHEMA,
    destroy=TEMPLATE_DESTROY_SCHEMA,
)
class TemplateViewSet(IntPkLookupMixin,viewsets.ModelViewSet):
    """CRUD de templates, anidado bajo suppliers/{supplier_pk}/templates/.

    Cada template mapea un formato de documento (xml/xlsx) de un supplier
    hacia un Layout destino. La unicidad de (supplier, layout,
    document_type) para templates activos la garantiza la constraint del
    modelo; acá no se duplica esa validación.
    """

    serializer_class = TemplateSerializer

    def get_queryset(self):
        return Template.objects.filter(
            supplier_id=self.kwargs["supplier_pk"], is_active=True
        ).select_related("layout")

    def perform_create(self, serializer):
        serializer.save(supplier_id=self.kwargs["supplier_pk"])


@auto_schema_view(
    list=TEMPLATE_FIELD_LIST_SCHEMA,
    create=TEMPLATE_FIELD_CREATE_SCHEMA,
    retrieve=TEMPLATE_FIELD_RETRIEVE_SCHEMA,
    update=TEMPLATE_FIELD_UPDATE_SCHEMA,
    partial_update=TEMPLATE_FIELD_PARTIAL_UPDATE_SCHEMA,
    destroy=TEMPLATE_FIELD_DESTROY_SCHEMA,
)
class TemplateFieldViewSet(IntPkLookupMixin,ViewSetSentryMixin, viewsets.ModelViewSet):
    """CRUD de los campos mapeados de un template.

    Anidado bajo suppliers/{supplier_pk}/templates/{template_pk}/fields/.
    El template se toma siempre de la URL. Se corre TemplateField.clean()
    en create/update para reforzar, a nivel API, que el layout_field
    pertenezca al layout del template (la constraint de unicidad de
    (template, layout_field) ya la cubre el modelo).
    """

    serializer_class = TemplateFieldSerializer

    def get_template(self):
        return Template.objects.get(
            pk=self.kwargs["template_pk"], supplier_id=self.kwargs["supplier_pk"]
        )

    def get_queryset(self):
        return (
            TemplateField.objects.filter(
                template_id=self.kwargs["template_pk"], is_active=True
            )
            .select_related("layout_field")
            .prefetch_related("rules__normalization_rule")
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["template"] = self.get_template()
        return ctx

    def perform_create(self, serializer):
        instance = serializer.save(template=self.get_template())
        self._full_clean(instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        self._full_clean(instance)

    @staticmethod
    def _full_clean(instance):
        try:
            instance.clean()
        except DjangoValidationError as exc:
            raise DRFValidationError({"detail": exc.messages}) from exc


@auto_schema_view(
    list=TEMPLATE_FIELD_RULE_LIST_SCHEMA,
    create=TEMPLATE_FIELD_RULE_CREATE_SCHEMA,
    retrieve=TEMPLATE_FIELD_RULE_RETRIEVE_SCHEMA,
    update=TEMPLATE_FIELD_RULE_UPDATE_SCHEMA,
    partial_update=TEMPLATE_FIELD_RULE_PARTIAL_UPDATE_SCHEMA,
    destroy=TEMPLATE_FIELD_RULE_DESTROY_SCHEMA,
    reorder=TEMPLATE_FIELD_RULE_REORDER_SCHEMA,
)
class TemplateFieldRuleViewSet(IntPkLookupMixin, ViewSetSentryMixin, viewsets.ModelViewSet):
    """CRUD de la cadena de normalization_rules de un template_field.

    Anidado bajo .../fields/{field_pk}/rules/. `sort_order` define el
    orden de ejecución al normalizar el valor extraído; se puede setear
    manualmente al crear/editar, o reordenar en bloque con la acción
    `reorder`.
    """

    serializer_class = TemplateFieldRuleSerializer

    def get_queryset(self):
        return TemplateFieldRule.objects.filter(
            template_field_id=self.kwargs["field_pk"]
        ).select_related("normalization_rule")

    def perform_create(self, serializer):
        serializer.save(template_field_id=self.kwargs["field_pk"])

    @action(detail=False, methods=["post"])
    def reorder(self, request, supplier_pk=None, template_pk=None, field_pk=None):
        """Reordena la cadena de reglas de un template_field.

        Body esperado: {"order": [rule_id_1, rule_id_2, ...]}. La posición
        en la lista determina el nuevo `sort_order` (1-indexed, orden de
        ejecución).
        """
        order = request.data.get("order")
        if not isinstance(order, list) or not order:
            return Response(
                {
                    "code": ErrorCodes.VALIDATION_ERROR,
                    "detail": "Se requiere 'order' como lista de IDs de TemplateFieldRule.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        rules_by_id = {
            r.id: r
            for r in TemplateFieldRule.objects.filter(
                template_field_id=field_pk, id__in=order
            )
        }
        if set(rules_by_id) != set(order):
            return Response(
                {
                    "code": ErrorCodes.VALIDATION_ERROR,
                    "detail": "Algunos IDs no pertenecen a este template_field o no existen.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        to_update = []
        for sort_order, rule_id in enumerate(order, start=1):
            rule = rules_by_id[rule_id]
            rule.sort_order = sort_order
            to_update.append(rule)

        with transaction.atomic():
            TemplateFieldRule.objects.bulk_update(to_update, ["sort_order"])

        return Response(TemplateFieldRuleSerializer(to_update, many=True).data)