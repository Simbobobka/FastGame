from Scrapers.AbstractScraper import AbstractScraper
from Scrapers.RedisClient import RedisScraperClient
from Scrapers.ScraperPlayWrightClient import ScraperClient


class IdsScraperWorker:
    """Generic worker for scraping game IDs (works with any scraper)"""

    def __init__(self, scraper: AbstractScraper):
        self.scraper = scraper

    async def run(self):
        """Execute ID scraping workflow"""
        await self.scraper.client.initiate()

        try:
            print(
                f"Worker {self.__class__.__name__} starting ID scraping for {self.scraper.scraper_name}..."
            )
            await self.scraper.scrape()
        except Exception as e:
            print(f"Error in {self.__class__.__name__}: {e}")
        finally:
            await self.scraper.client.close_connection()
