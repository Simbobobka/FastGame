import asyncio
import logging

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from ..AbstractScraper import AbstractScraper
from ..ScraperPlayWrightClient import ScraperClient
from ..SteamDB.Genres import Genres

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class SteamDBScraper(AbstractScraper):

    def __init__(self):
        """Initialize the scraper with a Playwright client."""
        self.client = ScraperClient()

    @property
    def base_url(self):
        """Return the full URL for the genre page."""
        return (
            "https://steamdb.info/tag/"
            + f"{Genres.SHOOTER.value}/"
            + "?min_reviews=500"
        )

    @property
    def browser(self):
        """Return the browser instance from the client."""
        return self.client.browser

    async def scrape(self):
        """Scrape app IDs from all pages of the genre."""
        await self.client.initiate()

        browser = self.client.browser
        page = await browser.new_page(user_agent=UserAgent().random)
        self.page = page

        await page.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
        """
        )

        max_page = 1

        try:
            await page.goto(self.base_url)
            logging.info(f"Loaded page: {await page.title()}")
            content = await page.content()

            max_page = await self.__get_number_of_pages__(content)
        except Exception as e:
            logging.error(f"Error during initialization: {e}")

        ids = []

        for page_num in range(max_page):

            content = await self.page.content()
            ids_current = await self.__extract_ids_per_page__(content)
            ids.append(ids_current)
            logging.info(f"Extracted {len(ids_current)} IDs from page {page_num+1}")
            await self.__move_to_next_page__(page_num)
            await asyncio.sleep(5)

        await self.client.close_connection()

    async def __move_to_next_page__(self, current):
        """Move to the specified page by clicking the paging button."""
        try:
            await self.page.locator(f'button[data-dt-idx="{current}"]').click()
            await self.page.wait_for_load_state("networkidle")
        except Exception as e:
            logging.error(f"Error {e}")

    async def __get_number_of_pages__(self, content):
        """Parse the HTML to get the total number of pages."""

        soup = BeautifulSoup(content, "html.parser")
        buttons = soup.find_all(class_="dt-paging-button")

        return int(buttons[-2].get_text(strip=True))

    async def __extract_ids_per_page__(self, content):
        """Extract app IDs from the current page's table rows."""

        soup = BeautifulSoup(content, "html.parser")
        rows = soup.select("tr.app[data-appid]")
        if not rows:
            logging.warning("No rows found on the page")
        app_ids = [row.get("data-appid") for row in rows]

        return app_ids

    async def __scrape_game_details(self, game_id):
        """scrape game details from SteamDB game page"""
        # TODO: implement game details scraper
        pass
