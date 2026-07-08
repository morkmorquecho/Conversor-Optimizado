from django.db import models

from core.models import BaseModel

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
class SupplierCatalogItem(BaseModel):
    """Supplier-specific catalog. Fully replaced on each update."""

    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="catalog_items"
    )
    tariff_code = models.CharField(max_length=64)
    commercial_description = models.CharField(max_length=512, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["supplier", "tariff_code"],
                name="unique_tariff_code_per_supplier",
            )
        ]
        indexes = [models.Index(fields=["supplier", "tariff_code"])]

    def __str__(self):
        return f"{self.supplier.code} - {self.tariff_code}"