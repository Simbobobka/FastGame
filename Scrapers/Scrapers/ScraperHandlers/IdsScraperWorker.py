from Scrapers.AbstractScraper import AbstractScraper


class IdsScraperWorker:
    """Generic worker for scraping game IDs (works with any scraper)"""

    def __init__(self, scraper: AbstractScraper):
        self.scraper = scraper

    async def run(self):
        """Execute ID scraping workflow"""
        print(f"Starting {self.scraper.scraper_name} ID scraper worker...")
        await self.scraper.client.initiate()

        try:
            await self.scraper.scrape()
            print(f"{self.scraper.scraper_name} ID scraping completed successfully")
        except Exception as e:
            print(f"Error in IdsScraperWorker: {e}")
            import traceback

            traceback.print_exc()
        finally:
            await self.scraper.client.close_connection()
            print(f"{self.scraper.scraper_name} ID scraper worker stopped")
