import json
from typing import Optional

from redis.asyncio import ConnectionPool, Redis

from Scrapers.settings import RedisConfig, get_config


class RedisScraperClient:
    """Redis client for scraper operations with common Redis patterns"""

    def __init__(self):

        config = get_config(RedisConfig)

        self.pool = ConnectionPool(
            host=config.host,
            port=config.port,
            db=config.db,
            max_connections=2,
            decode_responses=True,
        )
        self._redis: Optional[Redis] = None

    async def connect(self):
        """Initialize Redis connection"""
        if not self._redis:
            self._redis = Redis(connection_pool=self.pool)

        return self._redis

    async def close(self):
        """Close Redis connection and pool"""
        if self._redis:
            await self._redis.aclose()
            self._redis = None
        await self.pool.disconnect()

    async def save_last_scrape_page(self, scraper_name: str, genre: str, page: int):
        """Save last scraped page number for a genre"""
        key = f"{scraper_name}:last_scraped_page:{genre}"
        await self._redis.set(key, page)

    async def get_last_scrape_page(self, scraper_name: str, genre: str) -> int:
        """Get last scraped page number for a genre"""
        key = f"{scraper_name}:last_scraped_page:{genre}"
        page = await self._redis.get(key)
        return int(page) if page else 0
