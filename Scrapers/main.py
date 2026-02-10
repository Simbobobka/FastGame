import asyncio

from Scrapers.GOG.Gog import GogScraper
from Scrapers.RedisClient import RedisScraperClient
from Scrapers.SteamDB.SteamDB import SteamDBScraper


async def main():
    """Entry point for all scrapers with Redis integration"""

    redis_client = RedisScraperClient()
    await redis_client.connect()
    try:
        gog_scraper = GogScraper(redis_client=redis_client)
        await asyncio.gather(gog_scraper.scrape())
        # TODO: start scrapers as needed
    except Exception:
        pass  # TODO: Add proper error handling/logging
    finally:
        await redis_client.close()


if __name__ == "__main__":
    asyncio.run(main())
