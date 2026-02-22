from FastGame.settings import REDIS_QUEUE_URL
from redis import Redis

from ScrapersManagement.Entities.DetailsScrapingTask import DetailsScrapingTask


class RedisQueueService:
    """Service for managing Redsis queues for scraping tasks"""

    def __init__(self):
        self.redis_client = Redis.from_url(REDIS_QUEUE_URL)

    def push_task(self, task_data: DetailsScrapingTask):
        """Push a new task to the specified Redis queue"""
        queue_key = f"scraping:queue:{task_data.scraper_name}"
        self.redis_client.lpush(queue_key, task_data.model_dump_json())

    def check_queue_length(self, queue_key: str) -> int:
        """Check the number of tasks in the specified Redis queue"""
        return self.redis_client.llen(queue_key)

    def clear_queue(self, queue_key: str):
        """Clear all tasks from the specified Redis queue"""
        self.redis_client.delete(queue_key)
