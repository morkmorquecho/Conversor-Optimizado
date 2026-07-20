# templates/migrations/0002_seed_suzuki_casa_rojo.py
#
# Ajusta el nombre de archivo/número y las dependencies de abajo para que
# coincidan con tus migraciones reales (0001_initial de cada app).

from django.db import migrations


LAYOUT_FIELDS = [
    # (id, layout_id, name, sort_order)
    (1, 1, "NUMERO DE FACTURA", 1),
    (2, 1, "DESCRIPCION", 2),
    (3, 1, "CANTIDAD DE LA FACTURA", 3),
    (4, 1, "UNIDAD DE LA FACTURA", 4),
    (5, 1, "PRECIO DE LA PARTIDA", 5),
    (6, 1, "MODELO", 6),
    (7, 1, "MARCA", 7),
    (8, 1, "SUBMODELO", 8),
    (9, 1, "SERIE", 9),
    (10, 2, "CLAVE DEL PROVEEDOR", 1),
    (11, 2, "NO.FACTURA", 2),
    (12, 2, "FECHA DE FACTURA", 3),
    (13, 2, "MONTO DE FACTURA", 4),
    (14, 2, "MONEDA", 5),
    (15, 2, "INCOTERM", 6),
    (16, 2, "SUBDIVISION", 7),
    (17, 2, "CERT. ORIGEN", 8),
    (18, 2, "NUMERO DE PARTE", 9),
    (19, 2, "PAIS ORIGEN", 10),
    (20, 2, "PAIS VENDEDOR", 11),
    (21, 2, "FRACCION", 12),
    (22, 2, "DESCRIPCION", 13),
    (23, 2, "VALOR DE LA MERCANCIA", 14),
    (24, 2, "UMC", 15),
    (25, 2, "CANTIDAD DE UMC", 16),
    (26, 2, "CANTIDAD DE UMT", 17),
    (27, 2, "PREFERENCIA ARANCELARIA", 18),
    (28, 2, "Marca", 19),
    (29, 2, "Modelo", 20),
    (30, 2, "Submodelo", 21),
    (31, 2, "No. Serie", 22),
    (32, 2, "Descripción Cove", 23),
]

TEMPLATE_FIELDS = [
    # (id, template_id, layout_field_id, source_field, extraction_type, worksheet)
    (1, 1, 11, "I/V NO", "header_name", "Hoja1"),
    (2, 1, 12, "I/V DATE", "header_name", "Hoja1"),
    (3, 1, 13, "FOB AMOUNT", "header_name", "Hoja1"),
    (4, 1, 14, "CURRENCY", "header_name", "Hoja1"),
    (5, 1, 15, "TERM", "header_name", "Hoja1"),
    (6, 1, 18, "PART NO", "header_name", "Hoja1"),
    (7, 1, 25, "QTY", "header_name", "Hoja1"),
]


def seed_data(apps, schema_editor):
    Supplier = apps.get_model("catalogs", "Supplier")
    Layout = apps.get_model("layouts", "Layout")
    LayoutField = apps.get_model("layouts", "LayoutField")
    Template = apps.get_model("templates", "Template")
    TemplateField = apps.get_model("templates", "TemplateField")

    supplier = Supplier.objects.create(id=1, code="SUZUKI", name="Suzuki")

    Layout.objects.bulk_create(
        [
            Layout(id=1, code="casa_azul", name="Casa Azul", is_active=True),
            Layout(id=2, code="casa_rojo", name="Casa Rojo", is_active=True),
        ]
    )

    LayoutField.objects.bulk_create(
        [
            LayoutField(id=id_, layout_id=layout_id, name=name, sort_order=sort_order)
            for id_, layout_id, name, sort_order in LAYOUT_FIELDS
        ]
    )

    Template.objects.create(
        id=1,
        supplier=supplier,
        layout_id=2,  # casa_rojo
        name="susuki_casa_rojo_xlsx",
        document_type="xlsx",
        is_active=True,
    )

    TemplateField.objects.bulk_create(
        [
            TemplateField(
                id=id_,
                template_id=template_id,
                layout_field_id=layout_field_id,
                source_field=source_field,
                extraction_type=extraction_type,
                worksheet=worksheet,
            )
            for id_, template_id, layout_field_id, source_field, extraction_type, worksheet in TEMPLATE_FIELDS
        ]
    )


def unseed_data(apps, schema_editor):
    Supplier = apps.get_model("catalogs", "Supplier")
    Layout = apps.get_model("layouts", "Layout")
    LayoutField = apps.get_model("layouts", "LayoutField")
    Template = apps.get_model("templates", "Template")
    TemplateField = apps.get_model("templates", "TemplateField")

    # Reverse order: children before parents.
    TemplateField.objects.filter(
        id__in=[row[0] for row in TEMPLATE_FIELDS]
    ).delete()
    Template.objects.filter(id=1).delete()
    LayoutField.objects.filter(id__in=[row[0] for row in LAYOUT_FIELDS]).delete()
    Layout.objects.filter(id__in=[1, 2]).delete()
    Supplier.objects.filter(id=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalogs", "0001_initial"),
        ("layouts", "0001_initial"),
        ("templates", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_code=unseed_data),
    ]