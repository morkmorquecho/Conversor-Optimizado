from django.db import models


def active_unique_constraint(*fields, name=None):
    """
    Genera una UniqueConstraint condicionada a is_active=True.
    Uso: active_unique_constraint("name") o active_unique_constraint("template", "field_name")
    """
    if name is None:
        name = f"unique_active_{'_'.join(fields)}"
    return models.UniqueConstraint(
        fields=list(fields),
        condition=models.Q(is_active=True),
        name=name,
    )