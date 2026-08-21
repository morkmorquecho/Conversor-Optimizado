from __future__ import annotations
from lxml import etree
from extraction.services.base import BaseInvoiceExtractionService, ExtractionProcessingError
from templates.models import Template, TemplateField
from extraction.models import ExtractionBatch
from extraction.xpath_utils import resolve_xpath_values


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
        """Genera una unidad por cada coincidencia de los XPath repetidos.

        Los valores únicos del comprobante se replican en cada fila. Los XPath
        que apuntan a conceptos se alinean por posición para conservar los
        atributos de cada concepto en la misma fila.
        """
        try:
            root = etree.parse(uploaded_file).getroot()
        except etree.XMLSyntaxError as exc:
            raise ExtractionProcessingError(f"El archivo no es un XML válido: {exc}")

        values_by_field = {
            tf.id: resolve_xpath_values(root, tf.source_field.strip())
            for tf in self.template_fields
        }
        total_rows = max((len(values) for values in values_by_field.values()), default=0)

        for row_index in range(total_rows):
            raw_values = {}
            for template_field in self.template_fields:
                values = values_by_field[template_field.id]
                if len(values) == 1:
                    raw_values[template_field.id] = values[0]
                elif row_index < len(values):
                    raw_values[template_field.id] = values[row_index]
                else:
                    raw_values[template_field.id] = ""
            yield (row_index + 1, raw_values)
