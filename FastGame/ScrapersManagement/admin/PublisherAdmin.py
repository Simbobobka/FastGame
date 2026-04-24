from django.contrib import admin
from unfold.admin import ModelAdmin

from ..models.Publisher import Publisher


@admin.register(Publisher)
class PublisherAdmin(ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
