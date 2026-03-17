from django.contrib import admin

from .actions import (
    disable_details_scraper,
    disable_ids_scraper,
    enable_details_scraper,
    enable_ids_scraper,
    queue_selected_raw_ids,
    retry_selected_failed,
    sync_dead_letters,
    trigger_ids_scraper_now,
)
from .models.GameDetails import GameDetails
from .models.Platform import Platform
from .models.Publisher import Publisher
from .models.RawGamesIds import RawGamesIds
from .models.Source import Source


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
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
        trigger_ids_scraper_now,
        sync_dead_letters,
    )


@admin.register(RawGamesIds)
class RawGamesIdsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "source",
        "game_id",
        "genre",
        "status",
        "retry_count",
        "last_attempt_at",
    )
    list_filter = ("source", "status", "genre")
    search_fields = ("game_id", "genre")
    actions = (queue_selected_raw_ids, retry_selected_failed)


@admin.register(GameDetails)
class GameDetailsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "source",
        "release_date",
        "price",
        "is_free",
        "get_publishers",
        "url",
    )
    list_filter = ("source", "is_free")
    search_fields = ("name", "url")
    filter_horizontal = ("platforms", "publisher")

    def get_publishers(self, obj: GameDetails):
        return ", ".join(p.name for p in obj.publisher.all())

    get_publishers.short_description = "Publishers"


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
