from django.db import migrations


LAYOUT_FIELDS = [
    # (layout_code, name, sort_order)
    ("casa_azul", "NUMERO DE FACTURA", 1),
    ("casa_azul", "DESCRIPCION", 2),
    ("casa_azul", "CANTIDAD DE LA FACTURA", 3),
    ("casa_azul", "UNIDAD DE LA FACTURA", 4),
    ("casa_azul", "PRECIO DE LA PARTIDA", 5),
    ("casa_azul", "MODELO", 6),
    ("casa_azul", "MARCA", 7),
    ("casa_azul", "SUBMODELO", 8),
    ("casa_azul", "SERIE", 9),
    ("casa_rojo", "CLAVE DEL PROVEEDOR", 1),
    ("casa_rojo", "NO.FACTURA", 2),
    ("casa_rojo", "FECHA DE FACTURA", 3),
    ("casa_rojo", "MONTO DE FACTURA", 4),
    ("casa_rojo", "MONEDA", 5),
    ("casa_rojo", "INCOTERM", 6),
    ("casa_rojo", "SUBDIVISION", 7),
    ("casa_rojo", "CERT. ORIGEN", 8),
    ("casa_rojo", "NUMERO DE PARTE", 9),
    ("casa_rojo", "PAIS ORIGEN", 10),
    ("casa_rojo", "PAIS VENDEDOR", 11),
    ("casa_rojo", "FRACCION", 12),
    ("casa_rojo", "DESCRIPCION", 13),
    ("casa_rojo", "VALOR DE LA MERCANCIA", 14),
    ("casa_rojo", "UMC", 15),
    ("casa_rojo", "CANTIDAD DE UMC", 16),
    ("casa_rojo", "CANTIDAD DE UMT", 17),
    ("casa_rojo", "PREFERENCIA ARANCELARIA", 18),
    ("casa_rojo", "Marca", 19),
    ("casa_rojo", "Modelo", 20),
    ("casa_rojo", "Submodelo", 21),
    ("casa_rojo", "No. Serie", 22),
    ("casa_rojo", "Descripción Cove", 23),
]

TEMPLATE_FIELDS = [
    # (layout_field_name, source_field, extraction_type, worksheet)
    ("NO.FACTURA", "I/V NO", "header_name", "Hoja1"),
    ("FECHA DE FACTURA", "I/V DATE", "header_name", "Hoja1"),
    ("MONTO DE FACTURA", "FOB AMOUNT", "header_name", "Hoja1"),
    ("MONEDA", "CURRENCY", "header_name", "Hoja1"),
    ("INCOTERM", "TERM", "header_name", "Hoja1"),
    ("NUMERO DE PARTE", "PART NO", "header_name", "Hoja1"),
    ("CANTIDAD DE UMC", "QTY", "header_name", "Hoja1"),
]


def seed_data(apps, schema_editor):
    Supplier = apps.get_model("catalogs", "Supplier")
    Layout = apps.get_model("layouts", "Layout")
    LayoutField = apps.get_model("layouts", "LayoutField")
    Template = apps.get_model("templates", "Template")
    TemplateField = apps.get_model("templates", "TemplateField")

    supplier, _ = Supplier.objects.get_or_create(
        code="SUZUKI", defaults={"name": "Suzuki"}
    )

    layouts = {}
    for code, name in [("casa_azul", "Casa Azul"), ("casa_rojo", "Casa Rojo")]:
        layouts[code], _ = Layout.objects.get_or_create(
            code=code, defaults={"name": name, "is_active": True}
        )

    layout_fields = {}
    for layout_code, name, sort_order in LAYOUT_FIELDS:
        layout = layouts[layout_code]
        lf, _ = LayoutField.objects.get_or_create(
            layout=layout, name=name, defaults={"sort_order": sort_order}
        )
        # namespacing por layout, porque "DESCRIPCION" se repite en ambos layouts
        layout_fields[(layout_code, name)] = lf

    template, _ = Template.objects.get_or_create(
        supplier=supplier,
        layout=layouts["casa_rojo"],
        name="susuki_casa_rojo_xlsx",
        defaults={"document_type": "xlsx", "is_active": True},
    )

    for field_name, source_field, extraction_type, worksheet in TEMPLATE_FIELDS:
        TemplateField.objects.get_or_create(
            template=template,
            layout_field=layout_fields[("casa_rojo", field_name)],
            defaults={
                "source_field": source_field,
                "extraction_type": extraction_type,
                "worksheet": worksheet,
            },
        )


def unseed_data(apps, schema_editor):
    Supplier = apps.get_model("catalogs", "Supplier")
    Layout = apps.get_model("layouts", "Layout")

    # Ajusta on_delete de tus FKs: si son CASCADE, esto basta.
    # Si son PROTECT, necesitas borrar hijos primero en el orden correcto.
    Supplier.objects.filter(code="SUZUKI").delete()
    Layout.objects.filter(code__in=["casa_azul", "casa_rojo"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalogs", "0001_initial"),
        ("layouts", "0001_initial"),
        ("templates", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_code=unseed_data),
    ]