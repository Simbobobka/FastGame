from django.contrib import admin
from django.urls import path
from unfold.admin import ModelAdmin

from .actions import (
    disable_details_scraper,
    disable_ids_scraper,
    enable_details_scraper,
    enable_ids_scraper,
    queue_selected_raw_ids,
    retry_selected_failed,
    sync_dead_letters,
)
from .models.GameDetails import GameDetails
from .models.Platform import Platform
from .models.Publisher import Publisher
from .models.RawGamesIds import RawGamesIds
from .models.Source import Source


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


@admin.register(RawGamesIds)
class RawGamesIdsAdmin(ModelAdmin):
    list_display = (
        "id",
        "source",
        "game_id",
        "genre",
        "status",
        "retry_count",
        "last_attempt_at",
        "created_at",
        "updated_at",
    )
    list_filter = ("source", "status", "genre")
    search_fields = ("game_id", "genre")
    actions = (queue_selected_raw_ids, retry_selected_failed)


@admin.register(GameDetails)
class GameDetailsAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "source",
        "release_date",
        "price",
        "is_free",
        "get_publishers",
        "url",
        "created_at",
        "updated_at",
    )
    list_filter = ("source", "is_free")
    search_fields = ("name", "url")
    filter_horizontal = ("platforms", "publisher")
    fieldsets = (
        (
            "Game Overview",
            {
                "classes": ("gamedetails-overview",),
                "fields": ("name", "source", "url", "description"),
            },
        ),
        (
            "Commercial Info",
            {
                "classes": ("gamedetails-commerce",),
                "fields": ("price", "is_free", "release_date"),
            },
        ),
        (
            "Relations",
            {
                "classes": ("gamedetails-relations",),
                "fields": ("platforms", "publisher", "raw_games_ids"),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse", "gamedetails-meta"),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    class Media:
        css = {"all": ("admin/css/gamedetails_admin.css",)}

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ["created_at", "updated_at"]

        if obj:
            readonly_fields.extend(["publisher", "platforms", "raw_games_ids"])

        return tuple(readonly_fields)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("publisher")

    def get_publishers(self, obj: GameDetails):
        return ", ".join(p.name for p in obj.publisher.all())

    get_publishers.short_description = "Publishers"


@admin.register(Platform)
class PlatformAdmin(ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Publisher)
class PublisherAdmin(ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


def _get_urls(self):
    from .views_admin import statistics_view

    return [
        path("statistics/", self.admin_view(statistics_view), name="statistics"),
    ] + _original_get_urls(self)


_original_get_urls = admin.site.__class__.get_urls
admin.site.__class__.get_urls = _get_urls
