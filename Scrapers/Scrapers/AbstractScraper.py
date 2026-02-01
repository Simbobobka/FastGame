from abc import ABC, abstractmethod
from typing import Optional

from .RedisClient import RedisScraperClient


class AbstractScraper(ABC):
    """Base class for all scrapers with common interface"""

    def __init__(self, redis_client: Optional[RedisScraperClient] = None):
        """Initialize scraper with optional Redis client"""
        self.redis_client = redis_client

    @property
    @abstractmethod
    def browser(self):
        """Return the browser instance"""
        pass

    @property
    @abstractmethod
    def base_url(self):
        """Return the full URL."""
        pass

    @property
    @abstractmethod
    def scraper_name(self):
        """Return the scraper's name"""
        pass

    @abstractmethod
    async def scrape(self):
        """Main scraping logic - must be implemented by child classes"""
        pass
