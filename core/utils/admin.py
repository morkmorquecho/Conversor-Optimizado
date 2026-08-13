from django.contrib import admin
from django.utils.html import format_html


class BaseAdmin(admin.ModelAdmin):
    """
    Admin base para todos los modelos que heredan de BaseModel.
    Combina:
      - Visualización del campo 'id' en list_display.
      - Soporte para soft delete: ver todos los registros (incluyendo
        eliminados/inactivos), columna de estado y acciones de
        restaurar/desactivar.
    """

    exclude = ("deleted_at",)
    actions = ["action_restore", "action_deactivate"]

    # --- list_display: asegura que 'id' siempre aparezca ---
    def get_list_display(self, request):
        fields = super().get_list_display(request)

        if "id" not in fields:
            return ("id", *fields)

        return fields

    # --- queryset: usa all_objects para ver todo, respetando ordering ---
    def get_queryset(self, request):
        qs = self.model.all_objects.all()

        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)

        return qs

    # --- columna visual de estado ---
    def estado_registro(self, obj):
        if obj.is_deleted:
            return format_html(
                '<span style="color: red; font-weight: bold;">🗑 Eliminado ({})</span>',
                obj.deleted_at.strftime("%d/%m/%Y %H:%M"),
            )
        if not obj.is_active:
            return format_html('<span style="color: orange;">⚠ Inactivo</span>')
        return format_html('<span style="color: green;">✓ Activo</span>')

    estado_registro.short_description = "Estado"

    # --- acciones ---
    def action_restore(self, request, queryset):
        queryset.update(deleted_at=None, is_active=True)
        self.message_user(request, f"{queryset.count()} registro(s) restaurados.")

    action_restore.short_description = "Restaurar registros seleccionados"

    def action_deactivate(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} registro(s) desactivados.")

    action_deactivate.short_description = "Desactivar registros seleccionados"