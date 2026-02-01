import asyncio

from Scrapers.GOG.Gog import GogScraper
from Scrapers.RedisClient import RedisScraperClient
from Scrapers.SteamDB.SteamDB import SteamDBScraper


async def main():
    """Entry point for all scrapers with Redis integration"""

    redis_client = RedisScraperClient()

    try:
        steamdb_scraper = SteamDBScraper(redis_client=await redis_client.connect())
        gog_scraper = GogScraper(redis_client=await redis_client.connect())
        await asyncio.gather(steamdb_scraper.scrape(), gog_scraper.scrape())
        # TODO: start scrapers as needed
    except Exception:
        pass  # TODO: Add proper error handling/logging
    finally:
        await redis_client.close()


if __name__ == "__main__":
    asyncio.run(main())
