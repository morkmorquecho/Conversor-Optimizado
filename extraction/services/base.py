from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from io import BytesIO
from typing import Optional
import re
import openpyxl
from django.apps import apps
from django.utils import timezone
from catalogs.models import SupplierCatalog, SupplierCatalogColumnLayoutField, SupplierCatalogPivotMapping
from extraction.models import ExtractionBatch, ExtractionError as ExtractionErrorModel, ExtractionJob, ExtractionResult
from layouts.models import NormalizationRule
from templates.models import Template, TemplateField
from layouts.system_fields import SYSTEM_FIELD_REGISTRY


class ExtractionProcessingError(Exception):
    """Error de configuración o de datos que impide continuar el proceso."""


def _stringify_cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value).strip()


def apply_normalization_rule(rule: NormalizationRule, value: str) -> str:
    if value in (None, ""):
        return value
    config = rule.config or {}
    if rule.rule_type == NormalizationRule.RuleType.TRIM:
        return value.strip()
    if rule.rule_type == NormalizationRule.RuleType.UPPERCASE:
        return value.strip().upper()
    if rule.rule_type == NormalizationRule.RuleType.REGEX_REPLACE:
        pattern = config.get("pattern", "")
        replacement = config.get("replacement", "")
        return re.sub(pattern, replacement, value) if pattern else value
    if rule.rule_type == NormalizationRule.RuleType.DATE_FORMAT:
        input_format = config.get("input_format")
        output_format = config.get("output_format")
        if not input_format or not output_format:
            return value
        try:
            parsed = datetime.strptime(value.strip(), input_format)
        except ValueError:
            return value
        return parsed.strftime(output_format)
    if rule.rule_type == NormalizationRule.RuleType.VALUE_MAP:
        return _apply_value_map(config, value)
    return value


def _apply_value_map(config: dict, value: str) -> str:
    mapping = config.get("map", {}) or {}
    case_insensitive = config.get("case_insensitive", True)
    key = value.strip()
    if case_insensitive:
        mapping = {k.upper(): v for k, v in mapping.items()}
        key = key.upper()
    mapped_value = mapping.get(key, config.get("default", value))
    lookup_cfg = config.get("lookup")
    if not lookup_cfg:
        return mapped_value
    try:
        Model = apps.get_model(lookup_cfg["app_label"], lookup_cfg["model"])
        obj = Model.objects.get(**{lookup_cfg["match_field"]: mapped_value})
        return str(getattr(obj, lookup_cfg.get("result_field", "code")))
    except Exception:
        return mapped_value


def apply_normalization_chain(template_field: TemplateField, raw_value: str) -> str:
    value = raw_value
    rules = template_field.rules.select_related("normalization_rule").order_by("sort_order")
    for template_field_rule in rules:
        value = apply_normalization_rule(template_field_rule.normalization_rule, value)
    return value


class BaseInvoiceExtractionService(ABC):
    """
    Flujo común: normalización, resolución de catálogo por pivote, campos
    de sistema y generación del Excel de salida. Las subclases sólo
    resuelven cómo obtener los valores crudos desde su fuente.
    """
    file_format: str  # sobreescribir en cada subclase

    def __init__(self, template: Template, supplier_catalog: Optional[SupplierCatalog] = None):
        self.template = template
        self.supplier = template.supplier
        self.layout = template.layout
        self.supplier_catalog = supplier_catalog
        self.template_fields = list(self._load_template_fields())
        if not self.template_fields:
            raise ExtractionProcessingError("El template no tiene campos configurados para extracción.")
        self.layout_fields = list(self.layout.fields.order_by("sort_order"))
        self._catalog_mappings = []
        self._pivot_mapping = None
        if self.supplier_catalog is not None:
            self._catalog_mappings = self._resolve_catalog_mappings()
            self._pivot_mapping = (
                SupplierCatalogPivotMapping.objects
                .filter(template=self.template, supplier_catalog=self.supplier_catalog)
                .select_related("pivot_template_field__layout_field")
                .first()
            )

    # --- lo único que cambia por formato ---
    @abstractmethod
    def _load_template_fields(self):
        """TemplateFields relevantes para este tipo de extracción (HEADER_NAME o XPATH)."""

    @abstractmethod
    def _iter_source_units(self, source):
        """Debe yieldear (unit_index, raw_values_by_tf_id) por cada unidad a procesar."""

    # --- común ---
    def _resolve_catalog_mappings(self):
        return list(
            SupplierCatalogColumnLayoutField.objects.filter(
                column__supplier_catalog=self.supplier_catalog,
                layout_field__layout=self.layout,
            ).select_related("column", "layout_field")
        )

    def process(self, uploaded_file, source_file_name: str):
        units = list(self._iter_source_units(uploaded_file))
        if not units:
            raise ExtractionProcessingError("No se encontraron datos para el template seleccionado.")
        batch = ExtractionBatch.objects.create(
            supplier=self.supplier,
            source_file=source_file_name,
            file_format=self.file_format,
            status=ExtractionBatch.Status.PENDING,
            template=self.template,
            supplier_catalog=self.supplier_catalog,
            total_records=len(units),
        )
        jobs = [self._process_unit(batch, idx, raw) for idx, raw in units]
        successful = sum(1 for j in jobs if j.status == ExtractionJob.Status.PROCESSED)
        failed = sum(1 for j in jobs if j.status == ExtractionJob.Status.REVIEW)
        batch.status = ExtractionBatch.Status.REVIEW if failed else ExtractionBatch.Status.PROCESSED
        batch.successful_records = successful
        batch.failed_records = failed
        batch.processed_at = timezone.now()
        batch.save(update_fields=["status", "successful_records", "failed_records", "processed_at"])
        return self._build_output_workbook(jobs), batch

    def _process_unit(self, batch, unit_index: int, raw_values_by_tf_id: dict) -> ExtractionJob:
        job = ExtractionJob.objects.create(
            extraction_batch=batch, row_number=unit_index, status=ExtractionJob.Status.PENDING,
        )
        had_errors = False
        for tf in self.template_fields:
            raw_value = raw_values_by_tf_id.get(tf.id, "")
            normalized_value = apply_normalization_chain(tf, raw_value)
            ExtractionResult.objects.update_or_create(
                extraction_job=job, layout_field=tf.layout_field,
                defaults={"raw_value": raw_value, "normalized_value": normalized_value},
            )
        if self.supplier_catalog is not None and not self._fill_from_catalog(job):
            had_errors = True
        self._fill_system_fields(job, raw_values_by_tf_id)
        job.status = ExtractionJob.Status.REVIEW if had_errors else ExtractionJob.Status.PROCESSED
        job.processed_at = timezone.now()
        job.save(update_fields=["status", "processed_at"])
        return job

    def _fill_from_catalog(self, job: ExtractionJob) -> bool:
        if self._pivot_mapping is None:
            ExtractionErrorModel.objects.create(
                extraction_job=job,
                message=(f"No hay configuración de pivote para el template "
                          f"'{self.template.name}' y catálogo '{self.supplier_catalog.name}'."),
            )
            return False
        pivot_layout_field = self._pivot_mapping.pivot_template_field.layout_field
        pivot_result = ExtractionResult.objects.filter(extraction_job=job, layout_field=pivot_layout_field).first()
        pivot_value = (pivot_result.normalized_value or pivot_result.raw_value) if pivot_result else ""
        if not pivot_value:
            ExtractionErrorModel.objects.create(
                extraction_job=job, layout_field=pivot_layout_field,
                message="No se pudo obtener el valor pivote para consultar el catálogo.",
            )
            return False
        catalog_row = self.supplier_catalog.rows.filter(pivot_value=pivot_value).first()
        if catalog_row is None:
            ExtractionErrorModel.objects.create(
                extraction_job=job, layout_field=pivot_layout_field,
                message=f"No se encontró fila en el catálogo '{self.supplier_catalog.name}' para '{pivot_value}'.",
            )
            return False
        for mapping in self._catalog_mappings:
            value = _stringify_cell(catalog_row.data.get(mapping.column.source_name))
            ExtractionResult.objects.update_or_create(
                extraction_job=job, layout_field=mapping.layout_field,
                defaults={"raw_value": value, "normalized_value": value},
            )
        return True

    def _fill_system_fields(self, job: ExtractionJob, raw_values_by_tf_id: dict):
        for layout_field in self.layout_fields:
            if not layout_field.system_field_key:
                continue
            handler = SYSTEM_FIELD_REGISTRY.get(layout_field.system_field_key)
            if handler is None:
                continue
            value = _stringify_cell(handler(job, raw_values_by_tf_id))
            ExtractionResult.objects.update_or_create(
                extraction_job=job, layout_field=layout_field,
                defaults={"raw_value": value, "normalized_value": value},
            )

    def _build_output_workbook(self, jobs) -> bytes:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = self.layout.code[:31] or "output"
        ws.append([field.name for field in self.layout_fields])
        for job in jobs:
            results_by_field_id = {r.layout_field_id: (r.normalized_value or r.raw_value) for r in job.results.all()}
            ws.append([results_by_field_id.get(field.id, "") for field in self.layout_fields])
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()