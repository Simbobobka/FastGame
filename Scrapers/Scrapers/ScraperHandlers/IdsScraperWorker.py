from asyncio import sleep

from Scrapers.AbstractScraper import AbstractScraper
from Scrapers.utils.logger import get_logger


class IdsScraperWorker:
    """Generic worker for scraping game IDs (works with any scraper)"""

    def __init__(self, scraper: AbstractScraper, polling_interval: int = 5):
        self.scraper = scraper
        self.polling_interval = polling_interval
        self.logger = get_logger(f"worker.ids.{self.scraper.scraper_name}")

    async def run(self):
        """Execute ID scraping workflow"""
        self.logger.info(f"Starting {self.scraper.scraper_name} ID scraper worker...")
        if self.scraper.client:
            await self.scraper.client.initiate()

        try:
            while True:
                state = await self.scraper.redis_client.get_control_state(
                    self.scraper.scraper_name,
                    "ids",
                )
                if state == "stop":
                    self.logger.debug(
                        f"{self.scraper.scraper_name} IDs scraping is paused. Waiting for 'start' command..."
                    )
                    await sleep(self.polling_interval)
                    continue

                await self.scraper.scrape()
                await self.scraper.redis_client.set_control_state(
                    self.scraper.scraper_name, "ids", "stop"
                )
                self.logger.info(
                    f"{self.scraper.scraper_name} ID scraping completed successfully"
                )
        except Exception:
            self.logger.error("Error in IdsScraperWorker", exc_info=True)

        finally:
            if self.scraper.client:
                await self.scraper.client.close_connection()
            self.logger.info(f"{self.scraper.scraper_name} IDs control worker stopped")
