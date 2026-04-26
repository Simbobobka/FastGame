from django.contrib import admin
from unfold.admin import ModelAdmin

from ..models.GameDetails import GameDetails


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
