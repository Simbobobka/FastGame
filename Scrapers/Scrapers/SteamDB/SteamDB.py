import asyncio

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from ..AbstractScraper import AbstractScraper
from ..ScraperPlayWrightClient import ScraperClient
from ..SteamDB.Genres import Genres


class SteamDBScraper(AbstractScraper):

    def __init__(self):
        """Initialize the scraper with a Playwright client."""
        self.client = ScraperClient()

    @property
    def base_url(self):
        """Return the full URL"""
        return "https://steamdb.info/"

    @property
    def browser(self):
        """Return the browser instance from the client."""
        return self.client.browser

    async def scrape(self):
        """Scrape app IDs from all pages and detail info about game of the genre."""
        await self.client.initiate()

        try:
            await self.__scrape_game_ids()
            await self.__scrape_game_details()
        finally:
            await self.client.close_connection()

    async def __scrape_game_ids(self):
        """Scrape game IDs from all pages"""

        browser = self.client.browser
        self.page = await browser.new_page(user_agent=UserAgent().random)

        await self.page.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
        """
        )

        try:
            await self.page.goto(
                self.base_url + f"tag/{Genres.SHOOTER.value}/" + "?min_reviews=500"
            )
            content = await self.page.content()
            max_page = await self.__get_number_of_pages__(content)
        except Exception:
            pass

        ids = []

        for page_num in range(max_page):

            content = await self.page.content()
            ids_current = await self.__extract_ids_per_page__(content)
            ids.extend(ids_current)
            print(ids_current)
            await self.__move_to_next_page__(page_num + 1)
            await asyncio.sleep(3)

    async def __move_to_next_page__(self, current):
        """Move to the specified page by clicking the paging button."""
        try:
            await self.page.locator(f'button[data-dt-idx="{current}"]').click()
            await self.page.wait_for_load_state("networkidle")
        except Exception:
            pass

    async def __get_number_of_pages__(self, content) -> int:
        """Parse the HTML to get the total number of pages."""

        soup = BeautifulSoup(content, "html.parser")
        buttons = soup.find_all(class_="dt-paging-button")

        return int(buttons[-2].get_text(strip=True))

    async def __extract_ids_per_page__(self, content):
        """Extract app IDs from the current page's table rows."""

        soup = BeautifulSoup(content, "html.parser")
        rows = soup.select("tr.app[data-appid]")
        if not rows:
            pass
        app_ids = [row.get("data-appid") for row in rows]

        return app_ids

    async def __scrape_game_details(self):
        """scrape game details from SteamDB game page"""
        # TODO: implement game details scraper
        pass
