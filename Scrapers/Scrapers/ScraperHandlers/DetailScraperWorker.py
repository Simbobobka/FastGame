import asyncio
import json

import httpx

from Scrapers.AbstractScraper import AbstractScraper
from Scrapers.RedisClient import RedisScraperClient


class DetailScraperWorker:
    """Generic worker for scraping game details (works with any scraper)"""

    def __init__(self, scraper: AbstractScraper):
        self.scraper = scraper

    async def process_task(self, task_data: dict):
        """Process single game detail scraping task"""
        game_id = task_data["game_id"]
        # callback_url = "http://localhost:8002/app/scraped-game-details/"  # TODO: should be managed from config

        try:
            game_details = await self.scraper.scrape(game_id=game_id, page_number=0)
            print(f"Scraped details for game ID {game_id}: {game_details}")
        except Exception as e:
            await self._requeue_failed_task(task_data)
            print(f"Error scraping {game_id}: {e}")

    async def run(self):
        """Main worker loop - pulls tasks and distributes across contexts"""
        await self.scraper.client.initiate()
        queue_key = f"scraping:details:{self.scraper.scraper_name}"
        # await asyncio.sleep(100)

        try:
            while True:
                print(
                    f"Worker {self.__class__.__name__} checking for tasks in {queue_key}..."
                )
                await asyncio.sleep(
                    5
                )  # Polling interval - can be adjusted or made event-driven
                # task_jsons = self.redis_client.rpop(queue_key, self.concurrency)

                # if not task_jsons:
                #     await asyncio.sleep(5)
                #     continue

                # if isinstance(task_jsons, str):
                #     task_jsons = [task_jsons]

                # tasks = [json.loads(t) for t in task_jsons]

                # await asyncio.gather(
                #     *[self.process_task(t) for t in tasks],
                #     return_exceptions=True,
                # )
        except Exception as e:
            print(f"Error in {self.__class__.__name__}: {e}")
        finally:
            await self.scraper.client.close_connection()

    async def _send_result(self, callback_url: str, game_details):
        """Send scraped details back to Django"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            await client.post(callback_url, json=game_details.dict())

    async def _requeue_failed_task(self, task_data: dict):
        """Re-queue failed task for retry"""
        queue_key = f"scraping:details:{self.scraper.scraper_name}"
        self.scraper.redis_client.lpush(queue_key, json.dumps(task_data))
