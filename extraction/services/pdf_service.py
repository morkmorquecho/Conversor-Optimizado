from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import pdfplumber
import pytesseract
from decouple import config
from google import genai
from PIL import Image, ImageFilter, ImageOps

from extraction.extraction_prompts import SYSTEM_PROMPT, build_json_schema, build_user_prompt
from extraction.models import ExtractionBatch
from extraction.services.base import BaseInvoiceExtractionService, ExtractionProcessingError
from templates.models import Template, TemplateField


GEMINI_MODEL = "gemini-3.5-flash"
OCR_RASTER_RESOLUTION = 350
OCR_LANGUAGE = "spa"


@dataclass(frozen=True)
class PdfLlmPayload:
    extracted_text: str
    extracted_tables: list[list[list[str | None]]]
    system_prompt: str
    user_prompt: str
    json_schema: dict[str, Any]


class InvoicePdfExtractionService(BaseInvoiceExtractionService):
    file_format = ExtractionBatch.FileFormat.PDF

    def __init__(self, template: Template, supplier_catalog=None):
        if template.document_type != Template.DocumentType.PDF:
            raise ExtractionProcessingError("El template seleccionado no es de tipo PDF.")
        super().__init__(template, supplier_catalog)

    def _load_template_fields(self):
        return (
            self.template.fields.select_related("layout_field")
            .filter(
                extraction_type=TemplateField.ExtractionType.LLM_TEXT,
                is_active=True,
            )
        )

    def _iter_source_units(self, uploaded_file):
        payload = self.prepare_llm_payload(uploaded_file)
        llm_result = self._extract_with_gemini(payload)
        yield from self._build_source_units(llm_result)

    def prepare_llm_payload(self, uploaded_file) -> PdfLlmPayload:
        self._rewind(uploaded_file)
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                text_by_page = [page.extract_text() or "" for page in pdf.pages]
                tables = self._extract_tables(pdf)
                has_text = any(text.strip() for text in text_by_page)

                if not has_text:
                    # PDF escaneado / basado en imagen: no hay texto extraíble
                    # directamente, se usa OCR local con Tesseract (sin costo
                    # de API, corre dentro del contenedor).
                    text_by_page = self._ocr_pages(pdf)
        except Exception as exc:
            raise ExtractionProcessingError(
                "No se pudo leer el archivo como un PDF con texto extraíble."
            ) from exc
        finally:
            self._rewind(uploaded_file)

        extracted_text = "\n\n".join(
            f"--- PÁGINA {page_number} ---\n{text}"
            for page_number, text in enumerate(text_by_page, start=1)
        ).strip()

        if not any(text.strip() for text in text_by_page):
            raise ExtractionProcessingError(
                "No se pudo extraer texto del PDF, ni directamente ni vía OCR."
            )

        return PdfLlmPayload(
            extracted_text=extracted_text,
            extracted_tables=tables,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=build_user_prompt(
                template=self.template,
                extracted_text=extracted_text,
                extracted_tables=tables,
            ),
            json_schema=build_json_schema(self.template),
        )

    def _extract_tables(self, pdf) -> list[list[list[str | None]]]:
        if self.template.pdf_extraction_mode != Template.PdfExtractionMode.TEXT_AND_TABLES:
            return []

        tables = []
        for page in pdf.pages:
            tables.extend(page.extract_tables())
        return tables

    @staticmethod
    def _preprocess_for_ocr(image: Image.Image) -> Image.Image:
        """Mejora el contraste/nitidez antes de pasar la imagen a Tesseract."""
        gray = ImageOps.grayscale(image)
        # Aumenta contraste automáticamente
        gray = ImageOps.autocontrast(gray, cutoff=1)
        # Binariza: blanco/negro puro, ayuda mucho con texto escaneado
        threshold = 150
        binary = gray.point(lambda p: 255 if p > threshold else 0)
        # Nitidez leve
        binary = binary.filter(ImageFilter.SHARPEN)
        return binary

    @staticmethod
    def _ocr_pages(pdf, resolution: int = OCR_RASTER_RESOLUTION) -> list[str]:
        """Rasteriza cada página, la preprocesa, y le aplica OCR local con
        Tesseract. No hace ninguna llamada a la API de Gemini ni consume
        tokens."""
        texts: list[str] = []
        for page in pdf.pages:
            page_image = page.to_image(resolution=resolution)
            processed = InvoicePdfExtractionService._preprocess_for_ocr(page_image.original)
            text = pytesseract.image_to_string(processed, lang=OCR_LANGUAGE)
            texts.append(text or "")
        return texts

    @staticmethod
    def _rewind(uploaded_file) -> None:
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)

    @staticmethod
    def _gemini_api_key() -> str:
        api_key = config("GEMINI_API_KEY", default="").strip()
        if not api_key:
            raise ExtractionProcessingError(
                "GEMINI_API_KEY no está configurada en las variables de entorno."
            )
        return api_key

    def _extract_with_gemini(self, payload: PdfLlmPayload) -> dict[str, Any]:
        try:
            client = genai.Client(api_key=self._gemini_api_key())
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=payload.user_prompt,
                config={
                    "system_instruction": payload.system_prompt,
                    "response_mime_type": "application/json",
                    "response_json_schema": payload.json_schema,
                },
            )
            return json.loads(response.text)
        except ExtractionProcessingError:
            raise
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ExtractionProcessingError(
                "Gemini no devolvió una respuesta JSON válida para el template."
            ) from exc
        except Exception as exc:
            raise ExtractionProcessingError(
                "No fue posible obtener la extracción estructurada desde Gemini."
            ) from exc

    def _build_source_units(self, llm_result: dict[str, Any]):
        if not isinstance(llm_result, dict):
            raise ExtractionProcessingError("La respuesta estructurada de Gemini debe ser un objeto JSON.")

        header = llm_result.get("header", {})
        line_items = llm_result.get("line_items", [])
        if not isinstance(header, dict) or not isinstance(line_items, list):
            raise ExtractionProcessingError(
                "La respuesta de Gemini no coincide con la estructura esperada del template."
            )

        header_fields = [
            field for field in self.template_fields
            if field.scope == TemplateField.Scope.HEADER
        ]
        line_item_fields = [
            field for field in self.template_fields
            if field.scope == TemplateField.Scope.LINE_ITEM
        ]

        if line_item_fields:
            if not line_items:
                raise ExtractionProcessingError(
                    "Gemini no encontró renglones de partida para el template seleccionado."
                )
            for row_number, line_item in enumerate(line_items, start=1):
                if not isinstance(line_item, dict):
                    raise ExtractionProcessingError(
                        "Gemini devolvió un renglón de partida con formato inválido."
                    )
                yield row_number, self._raw_values(header_fields, header, line_item_fields, line_item)
            return

        yield 1, self._raw_values(header_fields, header, [], {})

    @staticmethod
    def _raw_values(header_fields, header, line_item_fields, line_item) -> dict[int, str]:
        values = {}
        for field in header_fields:
            values[field.id] = InvoicePdfExtractionService._as_raw_value(
                header.get(field.layout_field.name)
            )
        for field in line_item_fields:
            values[field.id] = InvoicePdfExtractionService._as_raw_value(
                line_item.get(field.layout_field.name)
            )
        return values

    @staticmethod
    def _as_raw_value(value: Any) -> str:
        if value is None:
            return ""
        if not isinstance(value, str):
            raise ExtractionProcessingError(
                "Gemini devolvió un valor que no es texto ni null."
            )
        return value