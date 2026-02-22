import asyncio

from Scrapers.GOG.Gog import GogScraper
from Scrapers.HttpRequestClient import HttpRequestClient
from Scrapers.RedisClient import RedisScraperClient
from Scrapers.ScraperHandlers.DetailScraperWorker import DetailScraperWorker
from Scrapers.ScraperHandlers.IdsScraperWorker import IdsScraperWorker
from Scrapers.ScrapersFactory import ScrapersFactory


class ScraperOrchestrator:
    """Manager for scrapers"""

    def __init__(self):
        self.workers = []
        self.redis_client = RedisScraperClient()
        self.http_client = HttpRequestClient()
        self._initialized = False

    async def initialize(self):
        """Initialize shared resources"""
        if self._initialized:
            return

        try:
            await self.redis_client.connect()
            await self.http_client.initialize()
        except Exception as e:
            print(f"Failed to initialize clients: {e}")
            raise

        self._initialized = True

    async def setup_workers(self):
        """Initialize all scraper workers with dependency injection"""
        self.workers = []

        ids_scrapers = ScrapersFactory.create_ids_scraper(
            scrapers=[GogScraper],
            redis_client=self.redis_client,
            http_client=self.http_client,
        )

        details_scrapers = ScrapersFactory.create_details_scraper(
            scrapers=[GogScraper],
            redis_client=self.redis_client,
            http_client=self.http_client,
        )

        for scraper in ids_scrapers:
            self.workers.append(IdsScraperWorker(scraper=scraper))

        for scraper in details_scrapers:
            self.workers.append(DetailScraperWorker(scraper=scraper))

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
        if self.http_client:
            await self.http_client.close()

        if self.redis_client:
            await self.redis_client.close()

        self._initialized = False
