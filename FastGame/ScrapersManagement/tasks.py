from celery import shared_task
from django.utils import timezone

from ScrapersManagement.Entities.DetailsScrapingTask import DetailsScrapingTask
from ScrapersManagement.Services.QueueService.RedisQueueService import RedisQueueService

from .models.constants import SCRAPING_STATUS
from .models.RawGamesIds import RawGamesIds
from .models.Source import Source


@shared_task
def set_details_scraper_state(source_id: int, enabled: bool) -> str:
    """Enable or disable the details scraper for a source by updating the database and setting control state in Redis."""
    source = Source.objects.get(id=source_id)
    source.details_scraper_enabled = enabled
    source.save(update_fields=["details_scraper_enabled", "updated_at"])

    RedisQueueService().set_control_state(
        source.name,
        "details",
        "start" if enabled else "stop",
    )
    return source.name


@shared_task
def set_ids_scraper_state(source_id: int, enabled: bool) -> str:
    """Enable or disable the IDs scraper for a source by updating the database and setting control state in Redis."""
    source = Source.objects.get(id=source_id)
    source.ids_scraper_enabled = enabled
    source.save(update_fields=["ids_scraper_enabled", "updated_at"])

    RedisQueueService().set_control_state(
        source.name,
        "ids",
        "start" if enabled else "stop",
    )
    return source.name


def _enqueue_raw_ids(queryset, status: str) -> int:
    queue_service = RedisQueueService()
    tasks = []
    queued_ids = []
    now = timezone.now()

    for raw_game_id in queryset.select_related("source"):
        if not raw_game_id.source.details_scraper_enabled:
            continue

        tasks.append(
            DetailsScrapingTask(
                game_id=raw_game_id.game_id,
                raw_id=raw_game_id.id,
                scraper_name=raw_game_id.source.name,
                genre=raw_game_id.genre,
                attempt=raw_game_id.retry_count,
                max_retries=raw_game_id.source.details_max_retries,
            )
        )
        queued_ids.append(raw_game_id.id)

    queue_service.push_tasks(tasks)

    if queued_ids:
        RawGamesIds.objects.filter(id__in=queued_ids).update(
            status=status,
            last_error="",
            last_attempt_at=now,
        )

    return len(queued_ids)


@shared_task
def enqueue_raw_game_ids(raw_game_ids_ids: list[int]) -> int:
    """Enqueue specific raw game IDs for detail scraping by pushing tasks to Redis. Only enqueues IDs that are not already scraped."""
    queryset = RawGamesIds.objects.filter(id__in=raw_game_ids_ids).exclude(
        status=SCRAPING_STATUS.SCRAPED
    )
    return _enqueue_raw_ids(queryset, status=SCRAPING_STATUS.IN_PROGRESS)


@shared_task
def retry_failed_details(
    source_id: int | None = None, raw_game_ids_ids: list[int] | None = None
) -> int:
    """Retry failed detail scraping tasks by re-queuing them in Redis. Can filter by source and/or specific raw game IDs."""
    queryset = RawGamesIds.objects.filter(status=SCRAPING_STATUS.FAILED)

    if source_id is not None:
        queryset = queryset.filter(source_id=source_id)

    if raw_game_ids_ids:
        queryset = queryset.filter(id__in=raw_game_ids_ids)

    return _enqueue_raw_ids(queryset, status=SCRAPING_STATUS.RETRY_WAITING)


@shared_task
def sync_dead_letter_queue(source_id: int, limit: int = 100) -> int:
    """Sync failed tasks from Redis dead letter queue back to the database for analysis and potential retries."""
    source = Source.objects.get(id=source_id)
    queue_service = RedisQueueService()
    failed_tasks = queue_service.pop_dead_letter_tasks(source.name, limit)

    if failed_tasks:
        now = timezone.now()
        RawGamesIds.objects.bulk_update(
            [
                RawGamesIds(
                    id=task["raw_id"],
                    status=SCRAPING_STATUS.FAILED,
                    retry_count=task.get("attempt", 0),
                    last_error=task.get("error", ""),
                    last_attempt_at=now,
                )
                for task in failed_tasks
            ],
            fields=["status", "retry_count", "last_error", "last_attempt_at"],
        )

    return len(failed_tasks)
