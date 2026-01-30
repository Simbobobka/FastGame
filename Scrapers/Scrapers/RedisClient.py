import os

from dotenv import load_dotenv
from redis.asyncio import ConnectionPool

load_dotenv()


class RedisScraperClient:
    def __init__(self):
        self.pool = ConnectionPool(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT")),
            db=int(os.getenv("REDIS_DB")),
            max_connections=2,
        )

    async def get_connection(self):
        return await self.pool.get_connection()
