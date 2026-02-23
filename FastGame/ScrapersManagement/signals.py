from typing import TYPE_CHECKING

from django.dispatch import Signal, receiver

from ScrapersManagement.Entities.DetailsScrapingTask import DetailsScrapingTask
from ScrapersManagement.Services.QueueService.RedisQueueService import RedisQueueService

if TYPE_CHECKING:
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

        for instance in instances:
            task_data = DetailsScrapingTask(
                game_id=instance.game_id,
                scraper_name=instance.source.name,
                genre=instance.genre,
                raw_id=instance.id,
            )
            queue_service.push_task(task_data)
    except Exception as e:
        print(f"Failed to push task to Redis queue: {e}")
