# catalogs/serializers.py
from rest_framework import serializers

from templates.models import Template

from .models import Supplier, SupplierCatalog, SupplierCatalogColumn, SupplierCatalogPivotMapping, SupplierCatalogRow


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

class ExcelDeduplicateSerializer(serializers.Serializer):
    file = serializers.FileField()
    column = serializers.CharField(
        help_text="Nombre de la columna usada para detectar renglones duplicados"
    )

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ["id", "code", "name"]



class SupplierCatalogColumnSerializer(serializers.Serializer):
    source_name = serializers.CharField(max_length=128)


class SupplierCatalogSerializer(serializers.ModelSerializer):
    """Para el listado: solo metadata, sin cargar todas las filas."""
    rows_count = serializers.IntegerField(source="rows.count", read_only=True)

    class Meta:
        model = SupplierCatalog
        fields = ["id", "name", "pivot_field_name", "rows_count", "is_active"]


class SupplierCatalogDetailSerializer(serializers.ModelSerializer):
    columns = SupplierCatalogColumnSerializer(many=True, required=False)

    class Meta:
        model = SupplierCatalog
        fields = ['id', 'name', 'pivot_field_name', 'columns', 'is_active']

    def create(self, validated_data):
        columns_data = validated_data.pop('columns', [])
        catalog = SupplierCatalog.objects.create(**validated_data)
        if columns_data:
            SupplierCatalogColumn.objects.bulk_create([
                SupplierCatalogColumn(supplier_catalog=catalog, source_name=c['source_name'])
                for c in columns_data
            ])
        return catalog

    def update(self, instance, validated_data):
        columns_data = validated_data.pop('columns', None)
        instance = super().update(instance, validated_data)
        if columns_data is not None:
            # reemplaza el set completo de columnas configuradas
            instance.columns.all().delete()
            SupplierCatalogColumn.objects.bulk_create([
                SupplierCatalogColumn(supplier_catalog=instance, source_name=c['source_name'])
                for c in columns_data
            ])
        return instance


class SupplierCatalogRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierCatalogRow
        fields = ["id", "pivot_value", "data"]

    def validate(self, attrs):
        # aprovecha el unique_pivot_value_per_catalog a nivel de request
        catalog = self.context["supplier_catalog"]
        pivot_value = attrs.get("pivot_value")
        if pivot_value:
            qs = SupplierCatalogRow.objects.filter(
                supplier_catalog=catalog, pivot_value=pivot_value
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"pivot_value": "Ya existe una fila con este valor pivote en el catálogo."}
                )
        return attrs


# serializers.py
class SupplierCatalogFromExcelSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    pivot_field_name = serializers.CharField(max_length=64)
    file = serializers.FileField()

    def validate(self, attrs):
        pivot_col = attrs["pivot_field_name"]
        uploaded_file = attrs["file"]

        try:
            df = pd.read_excel(uploaded_file, dtype=str)
        except Exception as exc:
            raise serializers.ValidationError(
                {"file": [f"No se pudo leer el archivo: {exc}"]}
            )

        df = df.dropna(how="all").fillna("")

        if pivot_col not in df.columns:
            raise serializers.ValidationError(
                {"pivot_field_name": [f"El archivo no tiene la columna '{pivot_col}'."]}
            )

        df = df[df[pivot_col].str.strip() != ""]

        duplicated = df[df[pivot_col].duplicated()][pivot_col].tolist()
        if duplicated:
            raise serializers.ValidationError(
                {"file": ["Valores de pivote duplicados: " + ", ".join(map(str, duplicated[:10]))]}
            )

        attrs["dataframe"] = df  # se pasa ya validado, sin releer el archivo en la view
        return attrs


class SupplierCatalogPivotMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierCatalogPivotMapping
        fields = ["id", "template", "pivot_template_field"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        catalog = self.context.get("catalog")
        if catalog:
            # Acota template a los del mismo proveedor del catálogo
            self.fields["template"].queryset = Template.objects.filter(
                supplier_id=catalog.supplier_id
            )

    def validate(self, attrs):
        template = attrs["template"]
        pivot_field = attrs["pivot_template_field"]
        if pivot_field.template_id != template.id:
            raise serializers.ValidationError(
                {"pivot_template_field": "Debe pertenecer al template indicado."}
            )
        return attrs