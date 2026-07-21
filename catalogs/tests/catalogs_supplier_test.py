# catalogs/tests.py
import io

from django.urls import reverse
from openpyxl import Workbook
from rest_framework import status
from rest_framework.test import APITestCase

from catalogs.models import Supplier, SupplierCatalog, SupplierCatalogColumn, SupplierCatalogRow


def build_excel_file(headers, rows):
    """Helper: builds an in-memory .xlsx file for upload tests."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(headers)
    for row in rows:
        sheet.append(row)

    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    buffer.name = "catalogo.xlsx"
    return buffer


class SupplierCatalogRowViewSetTests(APITestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(code="SUZUKI", name="Suzuki")
        self.catalog = SupplierCatalog.objects.create(
            supplier=self.supplier,
            name="Fracciones Suzuki",
            pivot_field_name="PART",
        )
        SupplierCatalogColumn.objects.create(
            supplier_catalog=self.catalog, source_name="FRACCION_TGCI"
        )
        SupplierCatalogColumn.objects.create(
            supplier_catalog=self.catalog, source_name="DESCRIPCION_COMERCIAL"
        )
        self.list_url = reverse("supplier-catalog-row-list")
        self.upload_url = reverse("supplier-catalog-row-upload")

    def test_list_filters_by_supplier_catalog(self):
        other_catalog = SupplierCatalog.objects.create(
            supplier=self.supplier, name="Otro catálogo", pivot_field_name="SKU"
        )
        SupplierCatalogRow.objects.create(
            supplier_catalog=self.catalog, pivot_value="ABC-123", data={}
        )
        SupplierCatalogRow.objects.create(
            supplier_catalog=other_catalog, pivot_value="XYZ-999", data={}
        )

        response = self.client.get(self.list_url, {"supplier_catalog": self.catalog.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["pivot_value"], "ABC-123")

    def test_create_row_manually(self):
        payload = {
            "supplier_catalog": self.catalog.id,
            "pivot_value": "ABC-123",
            "data": {"FRACCION_TGCI": "8708.99", "DESCRIPCION_COMERCIAL": "Filtro de aceite"},
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SupplierCatalogRow.objects.count(), 1)

    def test_patch_corrects_a_single_row(self):
        row = SupplierCatalogRow.objects.create(
            supplier_catalog=self.catalog,
            pivot_value="ABC-123",
            data={"FRACCION_TGCI": "8708.99"},
        )
        detail_url = reverse("supplier-catalog-row-detail", args=[row.id])

        response = self.client.patch(
            detail_url, {"data": {"FRACCION_TGCI": "8708.10"}}, format="json"
        )

        row.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(row.data["FRACCION_TGCI"], "8708.10")

    def test_upload_replaces_all_rows(self):
        SupplierCatalogRow.objects.create(
            supplier_catalog=self.catalog, pivot_value="OLD-999", data={}
        )
        excel_file = build_excel_file(
            headers=["PART", "FRACCION_TGCI", "DESCRIPCION_COMERCIAL"],
            rows=[
                ["ABC-123", "8708.99", "Filtro de aceite"],
                ["XYZ-456", "8708.29", "Amortiguador delantero"],
            ],
        )

        response = self.client.post(
            self.upload_url,
            {"supplier_catalog": self.catalog.id, "file": excel_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["created"], 2)
        self.assertEqual(SupplierCatalogRow.objects.count(), 2)
        # the old row must be gone — this was a full replace, not an append
        self.assertFalse(
            SupplierCatalogRow.objects.filter(pivot_value="OLD-999").exists()
        )

    def test_upload_missing_column_returns_400(self):
        excel_file = build_excel_file(
            headers=["PART", "FRACCION_TGCI"],  # falta DESCRIPCION_COMERCIAL
            rows=[["ABC-123", "8708.99"]],
        )

        response = self.client.post(
            self.upload_url,
            {"supplier_catalog": self.catalog.id, "file": excel_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["errors"]["code"], "VALIDATION_ERROR")
        self.assertIn("DESCRIPCION_COMERCIAL", response.data["errors"]["context"])
        self.assertEqual(SupplierCatalogRow.objects.count(), 0)

    def test_upload_duplicate_pivot_value_returns_400(self):
        excel_file = build_excel_file(
            headers=["PART", "FRACCION_TGCI", "DESCRIPCION_COMERCIAL"],
            rows=[
                ["ABC-123", "8708.99", "Filtro de aceite"],
                ["ABC-123", "8708.10", "Filtro duplicado"],
            ],
        )

        response = self.client.post(
            self.upload_url,
            {"supplier_catalog": self.catalog.id, "file": excel_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("duplicados", response.data["errors"]["context"])