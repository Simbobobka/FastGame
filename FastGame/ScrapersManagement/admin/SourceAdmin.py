from django.contrib import admin
from unfold.admin import ModelAdmin

from ..actions import (
    disable_details_scraper,
    disable_ids_scraper,
    enable_details_scraper,
    enable_ids_scraper,
    sync_dead_letters,
)
from ..models.Source import Source


@admin.register(Source)
class SourceAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "is_active",
        "ids_scraper_enabled",
        "details_scraper_enabled",
        "details_max_retries",
    )
    search_fields = ("name", "code")
    list_filter = ("is_active", "ids_scraper_enabled", "details_scraper_enabled")
    actions = (
        enable_details_scraper,
        disable_details_scraper,
        enable_ids_scraper,
        disable_ids_scraper,
        sync_dead_letters,
    )
