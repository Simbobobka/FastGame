from django.contrib import admin, messages

from .tasks import (
    enqueue_raw_game_ids,
    retry_failed_details,
    set_details_scraper_state,
    set_ids_scraper_state,
    sync_dead_letter_queue,
)


@admin.action(description="Enable details scraper")
def enable_details_scraper(modeladmin, request, queryset):
    count = queryset.count()
    for source in queryset:
        set_details_scraper_state.delay(source.id, True)
    modeladmin.message_user(
        request, f"Queued details scraper enable for {count} source(s)."
    )


@admin.action(description="Disable details scraper")
def disable_details_scraper(modeladmin, request, queryset):
    count = queryset.count()
    for source in queryset:
        set_details_scraper_state.delay(source.id, False)
    modeladmin.message_user(
        request,
        f"Queued details scraper disable for {count} source(s).",
        messages.WARNING,
    )


@admin.action(description="Enable IDs scraper")
def enable_ids_scraper(modeladmin, request, queryset):
    count = queryset.count()
    for source in queryset:
        set_ids_scraper_state.delay(source.id, True)
    modeladmin.message_user(
        request, f"Queued IDs scraper enable for {count} source(s)."
    )


@admin.action(description="Disable IDs scraper")
def disable_ids_scraper(modeladmin, request, queryset):
    count = queryset.count()
    for source in queryset:
        set_ids_scraper_state.delay(source.id, False)
    modeladmin.message_user(
        request, f"Queued IDs scraper disable for {count} source(s).", messages.WARNING
    )


@admin.action(description="Sync dead-letter queue")
def sync_dead_letters(modeladmin, request, queryset):
    count = queryset.count()
    for source in queryset:
        sync_dead_letter_queue.delay(source.id)
    modeladmin.message_user(request, f"Queued dead-letter sync for {count} source(s).")


@admin.action(description="Queue selected raw IDs")
def queue_selected_raw_ids(modeladmin, request, queryset):
    ids = list(queryset.values_list("id", flat=True))
    enqueue_raw_game_ids.delay(ids)
    modeladmin.message_user(request, f"Queued {len(ids)} raw ID(s) for processing.")


@admin.action(description="Retry failed raw IDs")
def retry_selected_failed(modeladmin, request, queryset):
    ids = list(queryset.values_list("id", flat=True))
    retry_failed_details.delay(raw_game_ids_ids=ids)
    modeladmin.message_user(request, f"Queued retry for {len(ids)} failed raw ID(s).")
