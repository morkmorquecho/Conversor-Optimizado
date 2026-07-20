from django.db import models

from core.models import BaseModel
from layouts.models import LayoutField

#Se registran a todos los provedores, la idea es que un provedor pueda tener diferentes tipo de templates pero siempre relacionados a su provedor
class Supplier(BaseModel):
    code = models.CharField(
        max_length=32, unique=True
    )
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"

#Catalogo de formato de monedas de casa
class Currency(BaseModel):
    code = models.CharField(max_length=8, unique=True)
    country = models.CharField(max_length=64)

    class Meta:
        verbose_name_plural = "Currencies"
        ordering = ["code"]

    def __str__(self):
        return self.code

#Catalogo de medidas de casa
class Umc(BaseModel):
    """Unit of measure code."""

    code = models.CharField(max_length=16, unique=True)
    description = models.CharField(max_length=255)

    class Meta:
        verbose_name = "UMC"
        verbose_name_plural = "UMCs"
        ordering = ["code"]

    def __str__(self):
        return self.code
    

#Catalogos de los provedores usados para terminar de llenar los layouts(archivos excel gigantes transformados a registros en la bd)
class SupplierCatalog(BaseModel):
    """A supplier-provided reference catalog (fracciones, descripciones, etc.).
 
    A supplier may have more than one catalog. Rows are looked up by a
    pivot value (e.g. part number) extracted from the invoice, to pull
    additional data that isn't present in the invoice itself.
    """
 
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="catalogs"
    )
    name = models.CharField(
        max_length=255, help_text="e.g. Catálogo de Fracciones Suzuki"
    )
    pivot_field_name = models.CharField(
        max_length=64,
        help_text="Column name inside the catalog file used as lookup key, e.g. 'PART'",
    )


 
    class Meta:
        ordering = ["supplier", "name"]
 
    def __str__(self):
        return f"{self.supplier.code} - {self.name}"
 
 
class SupplierCatalogColumn(BaseModel):
    """Describes one column of a SupplierCatalog and, optionally, which
    layout_field it feeds when used to fill the final output."""

    supplier_catalog = models.ForeignKey(
        SupplierCatalog, on_delete=models.CASCADE, related_name="columns"
    )
    source_name = models.CharField(
        max_length=128,
        help_text="Column name as it appears in the supplier's catalog file",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["supplier_catalog", "source_name"],
                name="unique_column_per_catalog",
            ),
        ]
        ordering = ["supplier_catalog", "source_name"]

    def __str__(self):
        return f"{self.supplier_catalog} - {self.source_name}"
class SupplierCatalogRow(BaseModel):
    """One row of a supplier catalog. Fully replaced on each update."""
 
    supplier_catalog = models.ForeignKey(
        SupplierCatalog, on_delete=models.CASCADE, related_name="rows"
    )
    pivot_value = models.CharField(
        max_length=128, help_text="Lookup key value, e.g. the part number"
    )
    data = models.JSONField(
        default=dict, help_text="source_name -> raw value, per SupplierCatalogColumn"
    )
 
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["supplier_catalog", "pivot_value"],
                name="unique_pivot_value_per_catalog",
            )
        ]
        indexes = [models.Index(fields=["supplier_catalog", "pivot_value"])]
 
    def __str__(self):
        return f"{self.supplier_catalog} - {self.pivot_value}"


class SupplierCatalogColumnLayoutField(models.Model):
    """Maps a catalog column to a layout_field, per layout.
 
    A catalog is reused across every layout that needs it (Casa Azul,
    Casa Roja, ...), and each layout has its own LayoutField rows, so a
    single column needs one mapping per layout — not a single fixed FK.
    This also covers the pivot column: it needs a mapping too, so
    extraction code knows which extracted layout_field value to match
    against SupplierCatalogRow.pivot_value for the layout being processed.
    """
 
    column = models.ForeignKey(
        SupplierCatalogColumn, on_delete=models.CASCADE, related_name="layout_fields"
    )
    layout_field = models.ForeignKey(
        "layouts.LayoutField", on_delete=models.PROTECT, related_name="+"
    )
 
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["column", "layout_field"],
                name="unique_layout_field_per_column",
            )
        ]
 
    def clean(self):
        from django.core.exceptions import ValidationError
 
        already_mapped = (
            SupplierCatalogColumnLayoutField.objects.filter(
                column=self.column, layout_field__layout=self.layout_field.layout
            )
            .exclude(pk=self.pk)
            .exists()
        )
        if already_mapped:
            raise ValidationError(
                "This column already has a layout_field mapped for this layout."
            )
 
    def __str__(self):
        return f"{self.column} -> {self.layout_field}"
 