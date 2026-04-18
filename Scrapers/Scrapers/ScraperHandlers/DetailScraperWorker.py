import asyncio
from asyncio import sleep
from typing import Optional

from Scrapers.AbstractScraper import AbstractScraper
from Scrapers.utils.DetailsScrapingTask import DetailsScrapingTask
from Scrapers.utils.logger import get_logger


class DetailScraperWorker:
    """Worker for scraping game details - distributes tasks concurrently"""

    def __init__(
        self, scraper: AbstractScraper, concurrency: int, polling_interval: int = 5
    ):
        self.scraper = scraper
        self.concurrency = concurrency
        self.polling_interval = polling_interval
        self.logger = get_logger(f"worker.details.{self.scraper.scraper_name}")

    async def process_task(
        self, task_data: DetailsScrapingTask, tab_index: int
    ) -> Optional[dict]:
        """Process single game detail scraping task on a specific tab"""
        game_id = task_data.game_id
        raw_id = task_data.raw_id

        try:
            self.logger.debug(f"Scraping game {game_id} on tab {tab_index}")

            await self.scraper.scrape(
                game_id=game_id, page_number=tab_index, raw_id=raw_id
            )
            self.logger.debug(f"Successfully scraped {game_id}")
        except Exception as e:
            self.logger.error(f"Error scraping {game_id}", exc_info=True)

            task_data.attempt += 1
            task_data.error = str(e)

            if task_data.attempt >= task_data.max_retries:
                await self.scraper.redis_client.push_dead_letter_task(
                    self.scraper.scraper_name,
                    task_data.model_dump_json(),
                )
                self.logger.warning(f"Max retries reached for {game_id}")
                return None

            await self._requeue_failed_task(task_data)

    async def run(self):
        """Main worker loop - pulls tasks and distributes across tabs"""
        if self.scraper.client:
            await self.scraper.client.initiate()

        queue_key = f"scraping:queue:{self.scraper.scraper_name}"

        self.logger.info(
            f"DetailScraperWorker started with {self.concurrency} concurrent workers"
        )

        try:
            while True:
                try:
                    state = await self.scraper.redis_client.get_control_state(
                        self.scraper.scraper_name,
                        "details",
                    )
                    if state == "stop":
                        await sleep(self.polling_interval)
                        continue

                    queue_length = await self.scraper.redis_client.get_queue_length(
                        queue_key
                    )

                    if queue_length == 0:
                        self.logger.debug(
                            f" No tasks in queue, sleeping for {self.polling_interval} seconds..."
                        )
                        await sleep(self.polling_interval)
                        continue

                    tasks_to_pull = min(self.concurrency, queue_length)
                    tasks: list[DetailsScrapingTask] = (
                        await self.scraper.redis_client.pop_tasks(
                            queue_key, tasks_to_pull
                        )
                    )

                    self.logger.debug(f"Processing {len(tasks)} tasks concurrently")

                    await asyncio.gather(
                        *[
                            self.process_task(task, tab_idx)
                            for tab_idx, task in enumerate(tasks)
                        ],
                        return_exceptions=True,
                    )

                    self.logger.info(f"Completed batch: {len(tasks)} tasks processed")
                    await asyncio.sleep(2)
                except Exception:
                    self.logger.error("Error processing batch", exc_info=True)
                    await sleep(self.polling_interval)
                    continue
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        finally:
            if self.scraper.client:
                await self.scraper.client.close_connection()
            self.logger.info("DetailScraperWorker stopped")

    async def _requeue_failed_task(self, task_data: DetailsScrapingTask):
        """Requeue failed task for retry"""
        queue_key = f"scraping:queue:{self.scraper.scraper_name}"
        await self.scraper.redis_client.requeue_task(
            queue_key, task_data.model_dump_json()
        )
        self.logger.warning(f"Requeued task: {task_data.game_id}")
