import asyncio

from Scrapers.SteamDB.SteamDB import SteamDBScraper


async def main():
    scraper = SteamDBScraper()
    await scraper.scrape()
    # delete after test


if __name__ == "__main__":
    asyncio.run(main())
