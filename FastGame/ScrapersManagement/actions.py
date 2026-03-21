from django.contrib import admin

from .tasks import (
    enqueue_raw_game_ids,
    retry_failed_details,
    set_details_scraper_state,
    set_ids_scraper_state,
    sync_dead_letter_queue,
)


@admin.action(description="Enable details scraper")
def enable_details_scraper(modeladmin, request, queryset):
    for source in queryset:
        set_details_scraper_state.delay(source.id, True)


@admin.action(description="Disable details scraper")
def disable_details_scraper(modeladmin, request, queryset):
    for source in queryset:
        set_details_scraper_state.delay(source.id, False)


@admin.action(description="Enable IDs scraper")
def enable_ids_scraper(modeladmin, request, queryset):
    for source in queryset:
        set_ids_scraper_state.delay(source.id, True)


@admin.action(description="Disable IDs scraper")
def disable_ids_scraper(modeladmin, request, queryset):
    for source in queryset:
        set_ids_scraper_state.delay(source.id, False)


@admin.action(description="Sync dead-letter queue")
def sync_dead_letters(modeladmin, request, queryset):
    for source in queryset:
        sync_dead_letter_queue.delay(source.id)


@admin.action(description="Queue selected raw IDs")
def queue_selected_raw_ids(modeladmin, request, queryset):
    enqueue_raw_game_ids.delay(list(queryset.values_list("id", flat=True)))


@admin.action(description="Retry failed raw IDs")
def retry_selected_failed(modeladmin, request, queryset):
    retry_failed_details.delay(
        raw_game_ids_ids=list(queryset.values_list("id", flat=True))
    )
