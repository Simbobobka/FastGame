import json

from FastGame.settings import REDIS_QUEUE_URL
from redis import Redis

from ScrapersManagement.Entities.DetailsScrapingTask import DetailsScrapingTask


class RedisQueueService:
    """Service for managing Redsis queues for scraping tasks"""

    def __init__(self):
        self.redis_client = Redis.from_url(REDIS_QUEUE_URL)

    def get_details_queue_key(self, scraper_name: str) -> str:
        return f"scraping:queue:{scraper_name}"

    def get_dead_letter_queue_key(self, scraper_name: str) -> str:
        return f"scraping:dead-letter:{scraper_name}"

    def get_control_key(self, scraper_name: str, target: str) -> str:
        return f"scraping:control:{scraper_name}:{target}"

    def get_ids_command_queue_key(self, scraper_name: str) -> str:
        return f"scraping:commands:{scraper_name}:ids"

    def push_task(self, task_data: DetailsScrapingTask):
        """Push a new task to the specified Redis queue"""
        queue_key = self.get_details_queue_key(task_data.scraper_name)
        self.redis_client.lpush(queue_key, task_data.model_dump_json())

    def push_dead_letter_task(self, task_data: DetailsScrapingTask):
        queue_key = self.get_dead_letter_queue_key(task_data.scraper_name)
        self.redis_client.lpush(queue_key, task_data.model_dump_json())

    def pop_dead_letter_tasks(self, scraper_name: str, count: int) -> list[dict]:
        queue_key = self.get_dead_letter_queue_key(scraper_name)
        tasks = []

        for _ in range(count):
            task = self.redis_client.rpop(queue_key)
            if not task:
                break
            tasks.append(json.loads(task))

        return tasks

    def set_control_state(self, scraper_name: str, target: str, state: str):
        key = self.get_control_key(scraper_name, target)
        self.redis_client.set(key, state)

    def check_queue_length(self, queue_key: str) -> int:
        """Check the number of tasks in the specified Redis queue"""
        return self.redis_client.llen(queue_key)

    def clear_queue(self, queue_key: str):
        """Clear all tasks from the specified Redis queue"""
        self.redis_client.delete(queue_key)
