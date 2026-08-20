from __future__ import annotations
from lxml import etree
from extraction.services.base import BaseInvoiceExtractionService, ExtractionProcessingError
from templates.models import Template, TemplateField
from extraction.models import ExtractionBatch
from extraction.xpath_utils import resolve_xpath_value


class InvoiceXmlExtractionService(BaseInvoiceExtractionService):
    file_format = ExtractionBatch.FileFormat.XML

    def __init__(self, template: Template, supplier_catalog=None):
        if template.document_type != Template.DocumentType.XML:
            raise ExtractionProcessingError("El template seleccionado no es de tipo XML.")
        super().__init__(template, supplier_catalog)

    def _load_template_fields(self):
        return (self.template.fields.select_related("layout_field")
                .filter(extraction_type=TemplateField.ExtractionType.XPATH))

    def _iter_source_units(self, uploaded_file):
        """Un XML = una unidad = un único ExtractionJob."""
        try:
            root = etree.parse(uploaded_file).getroot()
        except etree.XMLSyntaxError as exc:
            raise ExtractionProcessingError(f"El archivo no es un XML válido: {exc}")

        raw_values = {
            tf.id: (resolve_xpath_value(root, tf.source_field.strip()) or "")
            for tf in self.template_fields
        }
        yield (1, raw_values)