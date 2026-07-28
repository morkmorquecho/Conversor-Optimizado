from rest_framework import serializers


class ProcessInvoiceXlsxSerializer(serializers.Serializer):
    file = serializers.FileField()
    template_id = serializers.IntegerField()
    supplier_catalog_id = serializers.IntegerField(required=False, allow_null=True)