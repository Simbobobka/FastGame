import asyncio

from Scrapers.GOG.Gog import GogScraper

# from Scrapers.AbstractScraper import AbstractScraper
from Scrapers.RedisClient import RedisScraperClient
from Scrapers.ScraperHandlers.DetailScraperWorker import DetailScraperWorker
from Scrapers.ScraperHandlers.IdsScraperWorker import IdsScraperWorker
from Scrapers.ScraperPlayWrightClient import ScraperClient

# from Scrapers.SteamDB.SteamDB import SteamDBScraper


class ScraperOrchestrator:
    """Manager for scrapers"""

    def __init__(self):
        self.workers = []
        self.redis_client = RedisScraperClient()
        self._initialized = False

    async def initialize(self):
        """Initialize shared resources"""
        if self._initialized:
            return
        try:
            await self.redis_client.connect()
        except Exception as e:
            print(f"Failed to initialize Redis client: {e}")
            raise

        self._initialized = True

    async def setup_workers(self):
        """Initialize all scraper workers"""
        gog_id_browser = ScraperClient(tabs_quantity=1)
        gog_id_scraper = GogScraper(
            redis_client=self.redis_client,
            browser_client=gog_id_browser,
        )

        # Detail scraper: 1 browser with 5 pages
        gog_detail_browser = ScraperClient(tabs_quantity=5)
        gog_detail_scraper = GogScraper(
            redis_client=self.redis_client,
            browser_client=gog_detail_browser,
        )

        self.workers = [
            IdsScraperWorker(scraper=gog_id_scraper),
            DetailScraperWorker(scraper=gog_detail_scraper),
        ]

    async def run_all(self):
        """Run all workers concurrently"""
        await self.initialize()
        await self.setup_workers()

        try:
            tasks = [worker.run() for worker in self.workers]
            await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            await self._cleanup()

    async def _cleanup(self):
        """Clean up shared resources"""
        if self.redis_client:
            await self.redis_client.close()

        self._initialized = False
