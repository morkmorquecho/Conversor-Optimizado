# catalogs/views.py
import pandas as pd
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from catalogs.docs.schemas import SUPPLIER_CATALOG_ROW_CREATE_SCHEMA, SUPPLIER_CATALOG_ROW_DELETE_SCHEMA, SUPPLIER_CATALOG_ROW_PARTIAL_UPDATE_SCHEMA, SUPPLIER_CATALOG_ROW_RETRIEVE_SCHEMA, SUPPLIER_CATALOG_ROW_SCHEMA, SUPPLIER_CATALOG_ROW_UPDATE_SCHEMA, SUPPLIER_CATALOG_ROW_UPLOAD_SCHEMA
from core.docs.schema_utils import auto_schema_view

from .models import SupplierCatalogRow
from catalogs.serializers import SupplierCatalogRowSerializer, SupplierCatalogUploadSerializer

@auto_schema_view(
    list=SUPPLIER_CATALOG_ROW_SCHEMA,
    create=SUPPLIER_CATALOG_ROW_CREATE_SCHEMA,
    retrieve=SUPPLIER_CATALOG_ROW_RETRIEVE_SCHEMA,
    update=SUPPLIER_CATALOG_ROW_UPDATE_SCHEMA,
    partial_update=SUPPLIER_CATALOG_ROW_PARTIAL_UPDATE_SCHEMA,
    destroy=SUPPLIER_CATALOG_ROW_DELETE_SCHEMA,
    upload=SUPPLIER_CATALOG_ROW_UPLOAD_SCHEMA)
class SupplierCatalogRowViewSet(viewsets.ModelViewSet):
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
            df = pd.read_excel(uploaded_file, dtype=str).fillna("")
        except Exception as exc:
            return Response(
                {"detail": f"No se pudo leer el archivo: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        missing = expected_headers - set(df.columns)
        if missing:
            return Response(
                {
                    "detail": "Faltan columnas en el archivo: "
                    + ", ".join(sorted(missing))
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        duplicated = df[df[pivot_col].duplicated()][pivot_col].tolist()
        if duplicated:
            return Response(
                {
                    "detail": "Valores de pivote duplicados en el archivo: "
                    + ", ".join(map(str, duplicated[:10]))
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

