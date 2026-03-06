import asyncio

from Scrapers.AllKeyShop.AllKeyShop import AllKeyShopScraper
from Scrapers.GOG.Gog import GogScraper
from Scrapers.HttpRequestClient import HttpRequestClient
from Scrapers.RedisClient import RedisScraperClient
from Scrapers.ScrapersFactory import ScrapersFactory


class ScraperOrchestrator:
    """Manager for scrapers"""

    # Register all scraper classes here
    SCRAPER_CLASSES = [
        GogScraper,
        AllKeyShopScraper,
        # Add new scrapers here:
        # SteamScraper,
        # EpicScraper,
    ]

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

    def setup_workers(self):
        """Initialize all scraper workers using factory"""
        factory = ScrapersFactory(
            redis_client=self.redis_client,
            http_client=self.http_client,
        )

        self.workers = factory.create_all_workers(self.SCRAPER_CLASSES)

    async def run_all(self):
        """Run all workers concurrently"""
        await self.initialize()
        self.setup_workers()

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
