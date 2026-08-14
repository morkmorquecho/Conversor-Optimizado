# layouts/views.py
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from core.api_response.error_codes import ErrorCodes
from core.docs.schema_utils import auto_schema_view
from core.mixins import IntPkLookupMixin, ViewSetSentryMixin

from .docs.schemas import (
    LAYOUT_CREATE_SCHEMA,
    LAYOUT_DESTROY_SCHEMA,
    LAYOUT_FIELD_CREATE_SCHEMA,
    LAYOUT_FIELD_DESTROY_SCHEMA,
    LAYOUT_FIELD_LIST_SCHEMA,
    LAYOUT_FIELD_PARTIAL_UPDATE_SCHEMA,
    LAYOUT_FIELD_REORDER_SCHEMA,
    LAYOUT_FIELD_RETRIEVE_SCHEMA,
    LAYOUT_FIELD_UPDATE_SCHEMA,
    LAYOUT_LIST_SCHEMA,
    LAYOUT_PARTIAL_UPDATE_SCHEMA,
    LAYOUT_RETRIEVE_SCHEMA,
    LAYOUT_UPDATE_SCHEMA,
    NORMALIZATION_RULE_CREATE_SCHEMA,
    NORMALIZATION_RULE_DESTROY_SCHEMA,
    NORMALIZATION_RULE_LIST_SCHEMA,
    NORMALIZATION_RULE_PARTIAL_UPDATE_SCHEMA,
    NORMALIZATION_RULE_RETRIEVE_SCHEMA,
    NORMALIZATION_RULE_UPDATE_SCHEMA,
)
from .models import Layout, LayoutField, NormalizationRule
from .serializers import (
    LayoutDetailSerializer,
    LayoutFieldSerializer,
    LayoutSerializer,
    NormalizationRuleSerializer,
)


@auto_schema_view(
    list=LAYOUT_LIST_SCHEMA,
    retrieve=LAYOUT_RETRIEVE_SCHEMA,
    create=LAYOUT_CREATE_SCHEMA,
    update=LAYOUT_UPDATE_SCHEMA,
    partial_update=LAYOUT_PARTIAL_UPDATE_SCHEMA,
    destroy=LAYOUT_DESTROY_SCHEMA,
)
class LayoutViewSet(IntPkLookupMixin, viewsets.ModelViewSet):
    """CRUD de layouts destino (Casa Azul, Casa Roja, ...)."""

    queryset = Layout.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LayoutDetailSerializer
        return LayoutSerializer


@auto_schema_view(
    list=LAYOUT_FIELD_LIST_SCHEMA,
    create=LAYOUT_FIELD_CREATE_SCHEMA,
    retrieve=LAYOUT_FIELD_RETRIEVE_SCHEMA,
    update=LAYOUT_FIELD_UPDATE_SCHEMA,
    partial_update=LAYOUT_FIELD_PARTIAL_UPDATE_SCHEMA,
    destroy=LAYOUT_FIELD_DESTROY_SCHEMA,
    reorder=LAYOUT_FIELD_REORDER_SCHEMA,
)
class LayoutFieldViewSet(IntPkLookupMixin, ViewSetSentryMixin, viewsets.ModelViewSet):
    """CRUD de los campos de un layout.

    Anidado bajo layouts/{layout_pk}/fields/.
    """

    serializer_class = LayoutFieldSerializer

    def get_queryset(self):
        return LayoutField.objects.filter(
            layout_id=self.kwargs["layout_pk"], is_active=True
        )

    def perform_create(self, serializer):
        serializer.save(layout_id=self.kwargs["layout_pk"])

    def perform_destroy(self, instance):
        instance.hard_delete()

    @action(detail=False, methods=["post"])
    def reorder(self, request, layout_pk=None):
        order = request.data.get("order")
        if not isinstance(order, list) or not order:
            return Response(
                {"code": ErrorCodes.VALIDATION_ERROR,
                "detail": "Se requiere 'order' como lista de IDs de LayoutField."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        fields_by_id = {
            f.id: f
            for f in LayoutField.objects.filter(layout_id=layout_pk, id__in=order, is_active=True)
        }
        if set(fields_by_id) != set(order):
            return Response(
                {"code": ErrorCodes.VALIDATION_ERROR,
                "detail": "Algunos IDs no pertenecen a este layout o no existen."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            to_update = []
            for sort_order, field_id in enumerate(order, start=1):
                layout_field = fields_by_id[field_id]
                layout_field.sort_order = sort_order
                to_update.append(layout_field)
            LayoutField.objects.bulk_update(to_update, ["sort_order"])

        return Response(LayoutFieldSerializer(to_update, many=True).data)


@auto_schema_view(
    list=NORMALIZATION_RULE_LIST_SCHEMA,
    create=NORMALIZATION_RULE_CREATE_SCHEMA,
    retrieve=NORMALIZATION_RULE_RETRIEVE_SCHEMA,
    update=NORMALIZATION_RULE_UPDATE_SCHEMA,
    partial_update=NORMALIZATION_RULE_PARTIAL_UPDATE_SCHEMA,
    destroy=NORMALIZATION_RULE_DESTROY_SCHEMA,
)
class NormalizationRuleViewSet(IntPkLookupMixin, viewsets.ModelViewSet):
    """CRUD de reglas de normalización.

    No anidado: una regla es reutilizable entre distintos templates/fields,
    así que se administra de forma independiente y luego se encadena a un
    TemplateField vía TemplateFieldRule.
    """

    queryset = NormalizationRule.objects.filter(is_active=True)
    serializer_class = NormalizationRuleSerializer