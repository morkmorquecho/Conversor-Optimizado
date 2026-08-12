from django.core.management.base import BaseCommand
from catalogs.models import SupplierCatalogRow


class Command(BaseCommand):
    help = "Elimina físicamente (hard delete) todas las filas de un catálogo por su ID"

    def add_arguments(self, parser):
        parser.add_argument("catalog_id", type=int)

    def handle(self, *args, **options):
        catalog_id = options["catalog_id"]

        # all_objects es un Manager genérico (sin SoftDeleteQuerySet), así que
        # no tiene hard_delete(). all_with_deleted() sí regresa SoftDeleteQuerySet
        # e incluye filas ya soft-eliminadas antes.
        deleted, _ = SupplierCatalogRow.objects.all_with_deleted().filter(
            supplier_catalog_id=catalog_id
        ).hard_delete()

        self.stdout.write(
            self.style.SUCCESS(f"Eliminadas físicamente {deleted} filas del catálogo {catalog_id}")
        )