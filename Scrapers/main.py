import asyncio

from Scrapers.SteamDB.SteamDB import SteamDBScraper


async def main():
    scraper = SteamDBScraper()
    await scraper.scrape()


if __name__ == "__main__":
    asyncio.run(main())
