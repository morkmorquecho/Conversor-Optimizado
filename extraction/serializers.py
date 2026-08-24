from rest_framework import serializers


class ProcessInvoiceXlsxSerializer(serializers.Serializer):
    file = serializers.FileField()
    template_id = serializers.IntegerField()
    supplier_catalog_id = serializers.IntegerField(required=False, allow_null=True)

class ProcessInvoiceXmlSerializer(serializers.Serializer):
    file = serializers.FileField()
    template_id = serializers.IntegerField()
    supplier_catalog_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_file(self, f):
        if not f.name.lower().endswith(".xml"):
            raise serializers.ValidationError(f"El archivo '{f.name}' no es un .xml válido.")
        return f


class ProcessInvoicePdfSerializer(serializers.Serializer):
    file = serializers.FileField()
    template_id = serializers.IntegerField()
    supplier_catalog_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_file(self, f):
        if not f.name.lower().endswith(".pdf"):
            raise serializers.ValidationError(
                f"El archivo '{f.name}' no es un .pdf válido."
            )
        return f
