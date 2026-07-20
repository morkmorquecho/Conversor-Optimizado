from django.contrib import admin

class BaseAdmin(admin.ModelAdmin):
    exclude = ("deleted_at",)

    def get_list_display(self, request):
        fields = super().get_list_display(request)

        if "id" not in fields:
            return ("id", *fields)

        return fields