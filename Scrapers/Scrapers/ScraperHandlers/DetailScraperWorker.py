import asyncio
import traceback
from asyncio import sleep
from typing import Optional

from Scrapers.AbstractScraper import AbstractScraper
from Scrapers.utils.DetailsScrapingTask import DetailsScrapingTask


class DetailScraperWorker:
    """Worker for scraping game details - distributes tasks concurrently"""

    def __init__(
        self, scraper: AbstractScraper, concurrency: int, polling_interval: int = 5
    ):
        self.scraper = scraper
        self.concurrency = concurrency
        self.polling_interval = polling_interval

    async def process_task(
        self, task_data: DetailsScrapingTask, tab_index: int
    ) -> Optional[dict]:
        """Process single game detail scraping task on a specific tab"""
        game_id = task_data.game_id

        try:
            print(
                f"[{self.scraper.scraper_name}] Scraping game {game_id} on tab {tab_index}"
            )

            await self.scraper.scrape(game_id=game_id, page_number=tab_index)
            print(f"[{self.scraper.scraper_name}] Successfully scraped {game_id}")
        except Exception as e:
            print(f"[{self.scraper.scraper_name}] Error scraping {game_id}: {e}")
            traceback.print_exc()
            await self._requeue_failed_task(task_data)

    async def run(self):
        """Main worker loop - pulls tasks and distributes across tabs"""
        if self.scraper.client:
            await self.scraper.client.initiate()

        queue_key = f"scraping:queue:{self.scraper.scraper_name}"

        print(
            f"[{self.scraper.scraper_name}] DetailScraperWorker started with {self.concurrency} concurrent workers"
        )

        try:
            while True:
                try:
                    queue_length = await self.scraper.redis_client.get_queue_length(
                        queue_key
                    )

                    if queue_length == 0:
                        print(
                            f"[{self.scraper.scraper_name}] No tasks in queue, sleeping for {self.polling_interval} seconds..."
                        )
                        await sleep(self.polling_interval)
                        continue

                    tasks_to_pull = min(self.concurrency, queue_length)
                    tasks: list[DetailsScrapingTask] = (
                        await self.scraper.redis_client.pop_tasks(
                            queue_key, tasks_to_pull
                        )
                    )

                    print(
                        f"[{self.scraper.scraper_name}] Processing {len(tasks)} tasks concurrently"
                    )

                    await asyncio.gather(
                        *[
                            self.process_task(task, tab_idx)
                            for tab_idx, task in enumerate(tasks)
                        ],
                        return_exceptions=True,
                    )

                    print(
                        f"[{self.scraper.scraper_name}] Completed batch: {len(tasks)} tasks processed"
                    )
                except Exception as e:
                    print(f"[{self.scraper.scraper_name}] Error processing batch: {e}")
                    traceback.print_exc()
                    await sleep(self.polling_interval)
                    continue
        except KeyboardInterrupt:
            print(f"[{self.scraper.scraper_name}] Received shutdown signal")
        finally:
            if self.scraper.client:
                await self.scraper.client.close_connection()
            print(f"[{self.scraper.scraper_name}] DetailScraperWorker stopped")

    async def _requeue_failed_task(self, task_data: DetailsScrapingTask):
        """Requeue failed task for retry"""
        queue_key = f"scraping:queue:{self.scraper.scraper_name}"
        await self.scraper.redis_client.requeue_task(
            queue_key, task_data.model_dump_json()
        )
        print(f"[{self.scraper.scraper_name}] Requeued task: {task_data.game_id}")
