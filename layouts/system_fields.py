"""
Registro de funciones que resuelven campos de sistema.

Cada llave debe coincidir con un valor de LayoutField.SystemFieldKey.
Cada función recibe (job, row_data) — igual firma que el diccionario
SYSTEM_FIELD_HANDLERS anterior — y regresa el valor a guardar.
"""
from layouts.models import LayoutField


def _supplier_code(job, row_data):
    return job.extraction_batch.supplier.code
    # ← esta línea es idéntica a la que ya tenías en tu lambda original.
    #    No cambia la relación con Supplier, solo el lugar donde vive.


SYSTEM_FIELD_REGISTRY = {
    LayoutField.SystemFieldKey.SUPPLIER_CODE: _supplier_code,
}