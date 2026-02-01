import os
from typing import Optional

from dotenv import load_dotenv
from redis.asyncio import ConnectionPool, Redis

load_dotenv()


class RedisScraperClient:
    """Redis client for scraper operations with common Redis patterns"""

    def __init__(self):
        self.pool = ConnectionPool(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT")),
            db=int(os.getenv("REDIS_DB")),
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
