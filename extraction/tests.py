from io import BytesIO

from django.test import SimpleTestCase
from lxml import etree

from extraction.services.xml_service import InvoiceXmlExtractionService
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


class _TemplateField:
    def __init__(self, field_id, source_field):
        self.id = field_id
        self.source_field = source_field
