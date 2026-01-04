from Scrapers.Scrapers.ScraperPlayWrightClient import ScraperClient
from Scrapers.Scrapers.AbstractScraper import AbstractScraper


class SteamDBScraper(AbstractScraper):
    BASE_URL = "https://steamdb.info/"
    
    def __init__(self):
        self.client = ScraperClient()
    
    @property
    def browser(self):
        return self.client.browser

    async def scrape(self):
        await self.client.initiate()

        browser = self.client.browser
        page = await browser.new_page()
        
        await page.goto(self.BASE_URL)
        content = await page.content()
        
        await self.client.close_connection()
        
    
        return content