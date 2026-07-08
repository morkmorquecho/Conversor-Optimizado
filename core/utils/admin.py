from django.contrib import admin

class BaseAdmin(admin.ModelAdmin):
    exclude = ("deleted_at",)