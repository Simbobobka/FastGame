from Scrapers.Scrapers.ScraperPlayWrightClient import ScraperClient
from Scrapers.Scrapers.AbstractScraper import AbstractScraper
from fake_useragent import UserAgent


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
        page = await browser.new_page(user_agent=UserAgent().random)

        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
        """)

        await page.goto(self.BASE_URL)
        content = await page.content()
        
        await self.client.close_connection()
        
    
        return content