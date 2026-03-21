from asyncio import sleep

from Scrapers.AbstractScraper import AbstractScraper


class IdsScraperWorker:
    """Generic worker for scraping game IDs (works with any scraper)"""

    def __init__(self, scraper: AbstractScraper, polling_interval: int = 5):
        self.scraper = scraper
        self.polling_interval = polling_interval

    async def run(self):
        """Execute ID scraping workflow"""
        print(f"Starting {self.scraper.scraper_name} ID scraper worker...")
        if self.scraper.client:
            await self.scraper.client.initiate()

        try:
            while True:
                state = await self.scraper.redis_client.get_control_state(
                    self.scraper.scraper_name,
                    "ids",
                )
                if state == "stop":
                    print(
                        f"{self.scraper.scraper_name} IDs scraping is paused. Waiting for 'start' command..."
                    )
                    await sleep(self.polling_interval)
                    continue

                await self.scraper.scrape()
                await self.scraper.redis_client.set_control_state(
                    self.scraper.scraper_name, "ids", "completed"
                )
                print(f"{self.scraper.scraper_name} ID scraping completed successfully")
        except Exception as e:
            print(f"Error in IdsScraperWorker: {e}")
            import traceback

            traceback.print_exc()
        finally:
            if self.scraper.client:
                await self.scraper.client.close_connection()
            print(f"{self.scraper.scraper_name} IDs control worker stopped")
