from django.contrib import admin
from unfold.admin import ModelAdmin

from ..actions import queue_selected_raw_ids, retry_selected_failed
from ..models.RawGamesIds import RawGamesIds


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
