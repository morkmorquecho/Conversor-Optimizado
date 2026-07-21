

# catalogs/views.py
import io

from django.http import HttpResponse
import pandas as pd
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import APIView, action
from rest_framework.response import Response

from catalogs.docs.schemas import EXCEL_DEDUPLICATE_SCHEMA, SUPPLIER_CATALOG_ROW_CREATE_SCHEMA, SUPPLIER_CATALOG_ROW_DELETE_SCHEMA, SUPPLIER_CATALOG_ROW_PARTIAL_UPDATE_SCHEMA, SUPPLIER_CATALOG_ROW_RETRIEVE_SCHEMA, SUPPLIER_CATALOG_ROW_SCHEMA, SUPPLIER_CATALOG_ROW_UPDATE_SCHEMA, SUPPLIER_CATALOG_ROW_UPLOAD_SCHEMA
from core.api_response.error_codes import ErrorCodes
from core.docs.schema_utils import auto_schema, auto_schema_view
from core.mixins import ViewSetSentryMixin

from .models import SupplierCatalogRow
from .serializers import ExcelDeduplicateSerializer, SupplierCatalogRowSerializer, SupplierCatalogUploadSerializer

@auto_schema_view(
    list=SUPPLIER_CATALOG_ROW_SCHEMA,
    create=SUPPLIER_CATALOG_ROW_CREATE_SCHEMA,
    retrieve=SUPPLIER_CATALOG_ROW_RETRIEVE_SCHEMA,
    update=SUPPLIER_CATALOG_ROW_UPDATE_SCHEMA,
    partial_update=SUPPLIER_CATALOG_ROW_PARTIAL_UPDATE_SCHEMA,
    destroy=SUPPLIER_CATALOG_ROW_DELETE_SCHEMA,
    upload=SUPPLIER_CATALOG_ROW_UPLOAD_SCHEMA)
class SupplierCatalogRowViewSet(ViewSetSentryMixin,viewsets.ModelViewSet):
    """CRUD for individual catalog rows, plus a bulk-replace upload action.
 
    Config (Supplier, SupplierCatalog, SupplierCatalogColumn) is managed
    through the Django admin. This viewset only ever touches
    SupplierCatalogRow — the actual catalog data.
    """
 
    serializer_class = SupplierCatalogRowSerializer
 
    def get_queryset(self):
        queryset = SupplierCatalogRow.objects.select_related("supplier_catalog")
        supplier_catalog_id = self.request.query_params.get("supplier_catalog")
        if supplier_catalog_id:
            queryset = queryset.filter(supplier_catalog_id=supplier_catalog_id)
        return queryset
 
    @action(detail=False, methods=["post"])
    def upload(self, request):
        """Fully replace a catalog's rows from an uploaded Excel file.
 
        Expects a 'supplier_catalog' id and a 'file' in multipart form data.
        The file's headers must include the catalog's pivot_field_name plus
        every configured SupplierCatalogColumn.source_name.
        """
        serializer = SupplierCatalogUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        catalog = serializer.validated_data["supplier_catalog"]
        uploaded_file = serializer.validated_data["file"]
 
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
 
        # Drop fully blank rows (trailing/stray empty rows Excel sometimes
        # leaves behind) before validating anything else.
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
 
        # Rows with a blank pivot value aren't usable catalog entries either way.
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
    duplicados usando el pivot_field_name configurado en ese catálogo
    (no un valor que el usuario tenga que adivinar/escribir), y regresa
    el archivo corregido listo para descargar.
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
 
        # Same cleanup as the catalog upload: drop fully blank rows first,
        # then rows where the pivot column itself is blank.
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
    
