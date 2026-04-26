from django.contrib import admin
from unfold.admin import ModelAdmin

from ..models.Platform import Platform


@admin.register(Platform)
class PlatformAdmin(ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
