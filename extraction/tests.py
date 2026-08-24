from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase
from lxml import etree

from extraction.services.pdf_service import InvoicePdfExtractionService, PdfLlmPayload
from extraction.services.xml_service import InvoiceXmlExtractionService
from templates.models import Template, TemplateField
from extraction.xpath_utils import resolve_xpath_values


CFDI_NAMESPACE = "http://www.sat.gob.mx/cfd/4"


class XmlExtractionTests(SimpleTestCase):
    def test_resolve_xpath_values_returns_every_concept_value(self):
        root = etree.fromstring(
            f'''<cfdi:Comprobante xmlns:cfdi="{CFDI_NAMESPACE}" Folio="123">
                <cfdi:Conceptos>
                    <cfdi:Concepto NoIdentificacion="SKU-1" Cantidad="2" />
                    <cfdi:Concepto NoIdentificacion="SKU-2" Cantidad="3" />
                </cfdi:Conceptos>
            </cfdi:Comprobante>'''
        )
        path = (
            f".//{{{CFDI_NAMESPACE}}}Conceptos/"
            f"{{{CFDI_NAMESPACE}}}Concepto/@NoIdentificacion"
        )

        self.assertEqual(resolve_xpath_values(root, path), ["SKU-1", "SKU-2"])

    def test_iter_source_units_creates_one_row_per_concept_and_repeats_invoice_fields(self):
        service = InvoiceXmlExtractionService.__new__(InvoiceXmlExtractionService)
        service.template_fields = [
            _TemplateField(1, ".//@Folio"),
            _TemplateField(
                2,
                f".//{{{CFDI_NAMESPACE}}}Conceptos/"
                f"{{{CFDI_NAMESPACE}}}Concepto/@NoIdentificacion",
            ),
        ]
        xml = f'''<cfdi:Comprobante xmlns:cfdi="{CFDI_NAMESPACE}" Folio="123">
            <cfdi:Conceptos>
                <cfdi:Concepto NoIdentificacion="SKU-1" />
                <cfdi:Concepto NoIdentificacion="SKU-2" />
            </cfdi:Conceptos>
        </cfdi:Comprobante>'''

        rows = list(service._iter_source_units(BytesIO(xml.encode())))

        self.assertEqual(rows, [(1, {1: "123", 2: "SKU-1"}), (2, {1: "123", 2: "SKU-2"})])


class PdfExtractionTests(SimpleTestCase):
    def setUp(self):
        self.service = InvoicePdfExtractionService.__new__(InvoicePdfExtractionService)
        self.service.template_fields = [
            _PdfTemplateField(1, "folio", TemplateField.Scope.HEADER),
            _PdfTemplateField(2, "cantidad", TemplateField.Scope.LINE_ITEM),
        ]

    def test_build_source_units_repeats_header_for_each_line_item(self):
        units = list(
            self.service._build_source_units(
                {
                    "header": {"folio": "FAC-123"},
                    "line_items": [
                        {"cantidad": "2"},
                        {"cantidad": "5"},
                    ],
                }
            )
        )

        self.assertEqual(
            units,
            [
                (1, {1: "FAC-123", 2: "2"}),
                (2, {1: "FAC-123", 2: "5"}),
            ],
        )

    @patch("extraction.services.pdf_service.genai.Client")
    @patch.object(InvoicePdfExtractionService, "_gemini_api_key", return_value="test-key")
    def test_extract_with_gemini_requests_json_schema(self, mock_api_key, mock_client):
        response = Mock(text='{"header": {"folio": "FAC-123"}, "line_items": []}')
        mock_client.return_value.models.generate_content.return_value = response
        payload = PdfLlmPayload(
            extracted_text="Factura FAC-123",
            extracted_tables=[],
            system_prompt="system",
            user_prompt="user",
            json_schema={"type": "object"},
        )

        result = self.service._extract_with_gemini(payload)

        self.assertEqual(result["header"]["folio"], "FAC-123")
        mock_client.return_value.models.generate_content.assert_called_once_with(
            model="gemini-2.5-flash",
            contents="user",
            config={
                "system_instruction": "system",
                "response_mime_type": "application/json",
                "response_json_schema": {"type": "object"},
            },
        )


class _TemplateField:
    def __init__(self, field_id, source_field):
        self.id = field_id
        self.source_field = source_field


class _PdfTemplateField:
    def __init__(self, field_id, code, scope):
        self.id = field_id
        self.scope = scope
        self.layout_field = SimpleNamespace(code=code)
