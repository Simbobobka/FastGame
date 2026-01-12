from asyncio import sleep

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from Scrapers.AbstractScraper import AbstractScraper
from Scrapers.GOG.Genres import Genres
from Scrapers.ScraperPlayWrightClient import ScraperClient


class GogScraper(AbstractScraper):

    def __init__(self):
        self.client = ScraperClient()

    @property
    def base_url(self) -> str:
        """Return the base URL"""
        return "https://www.gog.com/"

    @property
    def browser(self):
        return self.client.browser

    async def scrape(self):
        await self.client.initiate()

        try:
            await self.__scrape_game_ids()
            await self.__scrape_game_details()
        finally:
            await self.client.close_connection()

    async def __scrape_game_ids(self):
        """scrape list of games from GOG homepage"""
        page = await self.browser.new_page(user_agent=UserAgent().random)
        await page.goto(self.base_url + f"en/games?genres={Genres.SHOOTER.value}")
        await sleep(2)

        pages = self.__scrape_pages_quantity(await page.content())
        self.game_ids = set()

        for page_number in range(2, pages + 1):
            self.__extract_game_ids(await page.content())
            await page.goto(
                self.base_url
                + f"en/games?genres={Genres.SHOOTER.value}&page={page_number}"
            )
            await sleep(2)

    async def __scrape_game_details(self, game_id):
        """scrape game details from GOG game page"""
        # TODO: implement game details scraper
        pass

    def __extract_game_ids(self, content):
        """extract game ids from page content"""
        soup = BeautifulSoup(content, "html.parser")

        grid_container = soup.find("div", class_="paginated-products-grid")
        game_cards = grid_container.find_all("product-tile")

        for card in game_cards:
            anchor = card.find("a", class_="product-tile")
            href = anchor.get("href")
            game_id = href.rstrip("/").split("/")[-1]
            self.game_ids.add(game_id)

    def __scrape_pages_quantity(self, content):
        """scrape quantity of pages from GOG homepage"""
        soup = BeautifulSoup(content, "html.parser")

        button = soup.find("button", attrs={"selenium-id": "smallPaginationPage"})

        if button and button.find("span"):
            return int(button.find("span").text.strip())

        return 1
