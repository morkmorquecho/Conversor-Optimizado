from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from catalogs.models import SupplierCatalog
from core.docs.schema_utils import auto_schema
from extraction.docs.schemas import PROCESS_INVOICE_PDF_SCHEMA, PROCESS_INVOICE_XLSX_SCHEMA, PROCESS_INVOICE_XML_SCHEMA
from templates.models import Template

from .serializers import (
    ProcessInvoicePdfSerializer,
    ProcessInvoiceXlsxSerializer,
    ProcessInvoiceXmlSerializer,
)
from extraction.services.base import ExtractionProcessingError
from extraction.services.pdf_service import InvoicePdfExtractionService
from extraction.services.xlsx_service import InvoiceXlsxExtractionService
from extraction.services.xml_service import InvoiceXmlExtractionService
XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

@auto_schema(**PROCESS_INVOICE_XLSX_SCHEMA)
class ProcessInvoiceXlsxView(APIView):
    """
    POST multipart/form-data:
      - file: excel de la factura
      - template_id: Template (document_type=xlsx) a usar
      - supplier_catalog_id: (opcional) SupplierCatalog a usar para el lookup
        por campo pivote.

    Responde con el xlsx generado.
    """

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = ProcessInvoiceXlsxSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        template = get_object_or_404(
            Template,
            pk=data["template_id"],
            is_active=True,
        )

        supplier_catalog = None

        catalog_id = data.get(
            "supplier_catalog_id"
        )

        if catalog_id:
            supplier_catalog = get_object_or_404(
                SupplierCatalog,
                pk=catalog_id,
                supplier=template.supplier,
            )

        try:
            service = InvoiceXlsxExtractionService(
                template=template,
                supplier_catalog=supplier_catalog,
            )

            output_bytes, batch = service.process(
                uploaded_file=data["file"],
                source_file_name=data["file"].name,
            )

        except ExtractionProcessingError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = HttpResponse(
            output_bytes,
            content_type=XLSX_CONTENT_TYPE,
        )

        filename = (
            f"{template.layout.code}_extraccion.xlsx"
        )

        response["Content-Disposition"] = (
            f'attachment; filename="{filename}"'
        )

        response["X-Extraction-Batch-Id"] = str(
            batch.id
        )

        return response



@auto_schema(**PROCESS_INVOICE_XML_SCHEMA)
class ProcessInvoiceXmlView(APIView):
    """
    POST multipart/form-data:
      - file: XML de la factura (CFDI)
      - template_id: Template (document_type=xml) a usar
      - supplier_catalog_id: (opcional) SupplierCatalog para el lookup por pivote

    El XML completo genera un único ExtractionJob. Responde con el xlsx generado.
    """

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = ProcessInvoiceXmlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        template = get_object_or_404(
            Template,
            pk=data["template_id"],
            is_active=True,
        )

        supplier_catalog = None
        catalog_id = data.get("supplier_catalog_id")
        if catalog_id:
            supplier_catalog = get_object_or_404(
                SupplierCatalog,
                pk=catalog_id,
                supplier=template.supplier,
            )

        try:
            service = InvoiceXmlExtractionService(
                template=template,
                supplier_catalog=supplier_catalog,
            )
            output_bytes, batch = service.process(
                uploaded_file=data["file"],
                source_file_name=data["file"].name,
            )
        except ExtractionProcessingError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response = HttpResponse(output_bytes, content_type=XLSX_CONTENT_TYPE)
        filename = f"{template.layout.code}_extraccion.xlsx"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response["X-Extraction-Batch-Id"] = str(batch.id)
        return response

@auto_schema(**PROCESS_INVOICE_PDF_SCHEMA)
class ProcessInvoicePdfView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = ProcessInvoicePdfSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        template = get_object_or_404(
            Template,
            pk=data["template_id"],
            is_active=True,
        )

        supplier_catalog = None
        catalog_id = data.get("supplier_catalog_id")
        if catalog_id:
            supplier_catalog = get_object_or_404(
                SupplierCatalog,
                pk=catalog_id,
                supplier=template.supplier,
            )

        try:
            output_bytes, batch = InvoicePdfExtractionService(
                template=template,
                supplier_catalog=supplier_catalog,
            ).process(
                uploaded_file=data["file"],
                source_file_name=data["file"].name,
            )
        except ExtractionProcessingError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = HttpResponse(output_bytes, content_type=XLSX_CONTENT_TYPE)
        response["Content-Disposition"] = (
            f'attachment; filename="{template.layout.code}_extraccion.xlsx"'
        )
        response["X-Extraction-Batch-Id"] = str(batch.id)
        return response
