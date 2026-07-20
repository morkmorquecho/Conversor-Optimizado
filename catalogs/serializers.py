# catalogs/serializers.py
from rest_framework import serializers

from .models import SupplierCatalog, SupplierCatalogRow


class SupplierCatalogRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierCatalogRow
        fields = ["id", "supplier_catalog", "pivot_value", "data", "created_at"]
        read_only_fields = ["created_at"]


class SupplierCatalogUploadSerializer(serializers.Serializer):
    """Payload for bulk-replacing a catalog's rows from an Excel file."""

    supplier_catalog = serializers.PrimaryKeyRelatedField(
        queryset=SupplierCatalog.objects.filter(is_active=True)
    )
    file = serializers.FileField()