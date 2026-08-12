# catalogs/views.py
import io

import pandas as pd
from django.db import transaction
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from catalogs.docs.schemas import (
    EXCEL_DEDUPLICATE_SCHEMA,
    SUPPLIER_CATALOG_CREATE_SCHEMA,
    SUPPLIER_CATALOG_DESTROY_SCHEMA,
    SUPPLIER_CATALOG_LIST_SCHEMA,
    SUPPLIER_CATALOG_PARTIAL_UPDATE_SCHEMA,
    SUPPLIER_CATALOG_RETRIEVE_SCHEMA,
    SUPPLIER_CATALOG_ROW_CREATE_SCHEMA,
    SUPPLIER_CATALOG_ROW_DESTROY_SCHEMA,
    SUPPLIER_CATALOG_ROW_LIST_SCHEMA,
    SUPPLIER_CATALOG_ROW_PARTIAL_UPDATE_SCHEMA,
    SUPPLIER_CATALOG_ROW_RETRIEVE_SCHEMA,
    SUPPLIER_CATALOG_ROW_UPDATE_SCHEMA,
    SUPPLIER_CATALOG_ROW_UPLOAD_SCHEMA,
    SUPPLIER_CATALOG_UPDATE_SCHEMA,
    SUPPLIER_LIST_SCHEMA,
)
from core.api_response.error_codes import ErrorCodes
from core.docs.schema_utils import auto_schema, auto_schema_view
from core.mixins import IntPkLookupMixin, ViewSetSentryMixin

from .models import Supplier, SupplierCatalog, SupplierCatalogColumn, SupplierCatalogRow
from .serializers import (
    ExcelDeduplicateSerializer,
    SupplierCatalogDetailSerializer,
    SupplierCatalogFromExcelSerializer,
    SupplierCatalogRowSerializer,
    SupplierCatalogSerializer,
    SupplierCatalogUploadSerializer,
    SupplierSerializer,
)


@auto_schema_view(
    list=SUPPLIER_LIST_SCHEMA,
)
class SupplierViewSet(IntPkLookupMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


@auto_schema_view(
    list=SUPPLIER_CATALOG_LIST_SCHEMA,
    retrieve=SUPPLIER_CATALOG_RETRIEVE_SCHEMA,
    create=SUPPLIER_CATALOG_CREATE_SCHEMA,
    update=SUPPLIER_CATALOG_UPDATE_SCHEMA,
    partial_update=SUPPLIER_CATALOG_PARTIAL_UPDATE_SCHEMA,
    destroy=SUPPLIER_CATALOG_DESTROY_SCHEMA,
)
class SupplierCatalogViewSet(IntPkLookupMixin, viewsets.ModelViewSet):
    """CRUD del catálogo en sí (nombre, pivot_field_name). Anidado bajo supplier."""

    serializer_class = SupplierCatalogDetailSerializer

    def get_queryset(self):
        return SupplierCatalog.objects.filter(
            supplier_id=self.kwargs["supplier_pk"], is_active=True
        )

    def get_serializer_class(self):
        if self.action == "list":
            return SupplierCatalogSerializer
        return SupplierCatalogDetailSerializer

    def perform_create(self, serializer):
        serializer.save(supplier_id=self.kwargs["supplier_pk"])

    # views.py
    @action(detail=False, methods=["post"])
    def from_excel(self, request, supplier_pk=None):
        serializer = SupplierCatalogFromExcelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data["name"]
        pivot_col = serializer.validated_data["pivot_field_name"]
        df = serializer.validated_data["dataframe"]
        column_names = [c for c in df.columns if c != pivot_col]

        with transaction.atomic():
            catalog = SupplierCatalog.objects.create(
                supplier_id=supplier_pk, name=name, pivot_field_name=pivot_col,
            )
            SupplierCatalogColumn.objects.bulk_create(
                [SupplierCatalogColumn(supplier_catalog=catalog, source_name=c) for c in column_names]
            )
            SupplierCatalogRow.objects.bulk_create([
                SupplierCatalogRow(
                    supplier_catalog=catalog,
                    pivot_value=row[pivot_col],
                    data={c: row[c] for c in column_names},
                )
                for _, row in df.iterrows()
            ])

        return Response(
            SupplierCatalogDetailSerializer(catalog).data,
            status=status.HTTP_201_CREATED,
        )


@auto_schema_view(
    list=SUPPLIER_CATALOG_ROW_LIST_SCHEMA,
    create=SUPPLIER_CATALOG_ROW_CREATE_SCHEMA,
    retrieve=SUPPLIER_CATALOG_ROW_RETRIEVE_SCHEMA,
    update=SUPPLIER_CATALOG_ROW_UPDATE_SCHEMA,
    partial_update=SUPPLIER_CATALOG_ROW_PARTIAL_UPDATE_SCHEMA,
    destroy=SUPPLIER_CATALOG_ROW_DESTROY_SCHEMA,
    upload=SUPPLIER_CATALOG_ROW_UPLOAD_SCHEMA,
)
class SupplierCatalogRowViewSet(IntPkLookupMixin, ViewSetSentryMixin, viewsets.ModelViewSet):
    """CRUD del contenido del catálogo (filas), anidado bajo supplier/catalog,
    más una acción bulk-replace por Excel.

    Config (Supplier, SupplierCatalog, SupplierCatalogColumn) se administra
    aparte, desde SupplierCatalogViewSet o el admin. Este viewset solo toca
    SupplierCatalogRow.
    """

    serializer_class = SupplierCatalogRowSerializer

    def get_catalog(self):
        return SupplierCatalog.objects.get(
            pk=self.kwargs["catalog_pk"], supplier_id=self.kwargs["supplier_pk"]
        )

    def get_queryset(self):
        qs = SupplierCatalogRow.objects.filter(
            supplier_catalog_id=self.kwargs["catalog_pk"]
        ).select_related("supplier_catalog")

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(pivot_value__icontains=search)

        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["supplier_catalog"] = self.get_catalog()
        return ctx

    def perform_create(self, serializer):
        serializer.save(supplier_catalog=self.get_catalog())

    @action(detail=False, methods=["post"])
    def upload(self, request, supplier_pk=None, catalog_pk=None):
        """Reemplaza por completo las filas del catálogo desde un Excel subido.

        El catálogo se toma de la URL (no del body). El archivo debe traer
        el pivot_field_name del catálogo más cada SupplierCatalogColumn
        configurada.
        """
        catalog = self.get_catalog()
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response(
                {
                    "code": ErrorCodes.VALIDATION_ERROR,
                    "detail": "No se recibió ningún archivo.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        columns = list(catalog.columns.all())
        pivot_col = catalog.pivot_field_name
        expected_headers = {pivot_col} | {c.source_name for c in columns}

        try:
            df = pd.read_excel(uploaded_file, dtype=str)
        except Exception as exc:
            return Response(
                {
                    "code": ErrorCodes.VALIDATION_ERROR,
                    "detail": f"No se pudo leer el archivo: {exc}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Elimina filas totalmente vacías antes de validar cualquier otra cosa.
        df = df.dropna(how="all").fillna("")

        missing = expected_headers - set(df.columns)
        if missing:
            return Response(
                {
                    "code": ErrorCodes.VALIDATION_ERROR,
                    "detail": "Faltan columnas en el archivo: "
                    + ", ".join(sorted(missing)),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filas con pivot vacío tampoco sirven como entradas de catálogo.
        df = df[df[pivot_col].str.strip() != ""]

        duplicated = df[df[pivot_col].duplicated()][pivot_col].tolist()
        if duplicated:
            return Response(
                {
                    "code": ErrorCodes.VALIDATION_ERROR,
                    "detail": "Valores de pivote duplicados en el archivo: "
                    + ", ".join(map(str, duplicated[:10])),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        rows = [
            SupplierCatalogRow(
                supplier_catalog=catalog,
                pivot_value=row[pivot_col],
                data={c.source_name: row[c.source_name] for c in columns},
            )
            for _, row in df.iterrows()
        ]

        with transaction.atomic():
            SupplierCatalogRow.objects.filter(supplier_catalog=catalog).delete()
            SupplierCatalogRow.objects.bulk_create(rows)

        return Response({"created": len(rows)}, status=status.HTTP_201_CREATED)


@auto_schema(**EXCEL_DEDUPLICATE_SCHEMA)
class ExcelDeduplicateView(APIView):
    """Sube un Excel y un supplier_catalog, quita renglones vacíos y
    duplicados usando el pivot_field_name configurado en ese catálogo, y
    regresa el archivo corregido listo para descargar.

    Esta vista queda plana (no anidada) porque es una herramienta de
    preprocesamiento independiente del CRUD de filas; por eso sigue
    recibiendo 'supplier_catalog' en el body en vez de tomarlo de la URL.
    """

    def post(self, request):
        serializer = SupplierCatalogUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        catalog = serializer.validated_data["supplier_catalog"]
        uploaded_file = serializer.validated_data["file"]
        pivot_col = catalog.pivot_field_name

        try:
            df = pd.read_excel(uploaded_file, dtype=str)
        except Exception as exc:
            return Response(
                {
                    "code": ErrorCodes.VALIDATION_ERROR,
                    "detail": f"No se pudo leer el archivo: {exc}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if pivot_col not in df.columns:
            return Response(
                {
                    "code": ErrorCodes.VALIDATION_ERROR,
                    "detail": f"El archivo no trae la columna pivote '{pivot_col}' "
                    f"configurada para este catálogo. Columnas disponibles: "
                    f"{', '.join(df.columns)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        df = df.dropna(how="all").fillna("")
        df = df[df[pivot_col].str.strip() != ""]

        rows_before = len(df)
        df = df.drop_duplicates(subset=[pivot_col], keep="first")
        removed = rows_before - len(df)

        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)

        response = HttpResponse(
            buffer.read(),
            content_type=(
                "application/vnd.openxmlformats-officedocument"
                ".spreadsheetml.sheet"
            ),
        )
        response["Content-Disposition"] = (
            'attachment; filename="archivo_sin_duplicados.xlsx"'
        )
        response["X-Duplicates-Removed"] = str(removed)
        return response

