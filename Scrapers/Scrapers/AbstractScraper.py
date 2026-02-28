from abc import ABC, abstractmethod
from typing import Optional

from Scrapers.HttpRequestClient import HttpRequestClient
from Scrapers.RedisClient import RedisScraperClient
from Scrapers.ScraperPlayWrightClient import ScraperClient


class AbstractScraper(ABC):
    """Base class for all scrapers with dependency injection"""

    requires_browser: bool = True

    def __init__(
        self,
        redis_client: RedisScraperClient,
        http_client: HttpRequestClient,
        browser_client: Optional[ScraperClient] = None,
    ):
        """Initialize scraper with injected dependencies"""
        self.redis_client = redis_client
        self.client = browser_client
        self.http_client = http_client

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Return the base URL for the scraper"""
        pass

    @property
    @abstractmethod
    def scraper_name(self) -> str:
        """Return the scraper's unique identifier"""
        pass

    @abstractmethod
    async def scrape(self, game_id: str = None, page_number: int = 0):
        """Main scraping logic - must be implemented by child classes"""
        pass

    async def send_data(self, url: str, data: dict) -> int:
        """Send scraped data via HTTP with retry logic"""
        return await self.http_client.send_with_backoff(url, data)
