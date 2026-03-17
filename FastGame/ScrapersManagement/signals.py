from typing import TYPE_CHECKING

from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from django.utils import timezone

from ScrapersManagement.Entities.DetailsScrapingTask import DetailsScrapingTask
from ScrapersManagement.models.constants import SCRAPING_STATUS
from ScrapersManagement.Services.QueueService.RedisQueueService import RedisQueueService

if TYPE_CHECKING:
    from ScrapersManagement.models.GameDetails import GameDetails
    from ScrapersManagement.models.RawGamesIds import RawGamesIds

post_bulk_create = Signal()


@receiver(post_bulk_create)
def raw_games_ids_bulk_saved_handler(sender, instances: list["RawGamesIds"], **kwargs):
    """
    Push game IDs to Redis queue for detail scraping when new IDs are scraped.
    The DetailScraperWorker in the Scrapers service will pick up these tasks.
    """
    if not instances:
        return

    try:
        queue_service = RedisQueueService()
        queued_ids = []

        for instance in instances:
            if not instance.source.details_scraper_enabled:
                continue

            task_data = DetailsScrapingTask(
                game_id=instance.game_id,
                scraper_name=instance.source.name,
                genre=instance.genre,
                raw_id=instance.id,
                attempt=instance.retry_count,
                max_retries=instance.source.details_max_retries,
            )
            queue_service.push_task(task_data)
            queued_ids.append(instance.id)

        if queued_ids:
            sender.objects.filter(id__in=queued_ids).update(
                status=SCRAPING_STATUS.IN_PROGRESS,
                last_error="",
                last_attempt_at=timezone.now(),
            )
    except Exception as e:
        print(f"Failed to push task to Redis queue: {e}")


@receiver(post_save, sender="ScrapersManagement.GameDetails")
def game_details_saved_handler(sender, instance: "GameDetails", **kwargs):
    """
    Mark raw games IDS as scraped when game details are saved
    """
    if not instance.raw_games_ids:
        raise ValueError(
            "GameDetails instance must be linked to a RawGamesIds instance"
        )

    instance.raw_games_ids.status = SCRAPING_STATUS.SCRAPED
    instance.raw_games_ids.last_error = ""
    instance.raw_games_ids.save()
