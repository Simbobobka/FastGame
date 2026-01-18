from asyncio import sleep
from datetime import datetime

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from playwright.async_api import Page

from Scrapers.AbstractScraper import AbstractScraper
from Scrapers.GOG.Enums.Genres import Genres
from Scrapers.ScraperPlayWrightClient import ScraperClient
from Scrapers.utils.Enums.SupportedOsSystems import SupportedOSSystems
from Scrapers.utils.exception import ScraperError
from Scrapers.utils.GameModel import GameModel


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

        except AttributeError as e:
            raise ScraperError("GOG") from e

            await self.__scrape_game_details(
                "against_the_storm"
            )  # TODO: temporary hardcoded
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
            await page.wait_for_load_state("domcontentloaded")

    async def __scrape_game_details(self, game_id: str) -> GameModel:
        """scrape game details from GOG game page"""
        page = await self.browser.new_page(user_agent=UserAgent().random)
        await page.goto(self.base_url + f"en/game/{game_id}")
        await page.wait_for_load_state("domcontentloaded")

        await self.__accept_cookies(page)

        game_details = self.__extract_game_details(await page.content())

        return game_details

    async def __accept_cookies(self, page: Page):
        """Accept cookies on the page if the prompt appears"""
        try:
            cookie_dialog = await page.query_selector("#CybotCookiebotDialog")

            if cookie_dialog:
                is_visible = await cookie_dialog.is_visible()

                if is_visible:
                    accept_button = await page.query_selector(
                        "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"
                    )

                    if accept_button:
                        await accept_button.click()
                        await sleep(1)
        except Exception:
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

    def __extract_game_details(self, content) -> GameModel:
        """extract game details from game page content"""
        game_details = GameModel()
        soup = BeautifulSoup(content, "html.parser")

        game_details.name = soup.find(
            "h1", class_="productcard-basics__title"
        ).text.strip()
        game_details.url = soup.find("link", rel="canonical")["href"]

        company_rows = soup.find_all(
            "div", class_="table__row details__rating details__row"
        )

        for row in company_rows:
            label = row.find("div", class_="details__category table__row-label")

            if label and "Release date:" in label.text:
                content_div = row.find(
                    "div", class_="details__content table__row-content"
                )
                date_span = content_div.find("span", class_="ng-binding")
                if date_span:
                    date_str = date_span.text.strip()
                    date_obj = datetime.strptime(date_str, "%B %d, %Y")
                    game_details.release_date = date_obj.strftime("%d.%m.%Y")

            elif label and "Company:" in label.text:
                content_div = row.find(
                    "div", class_="details__content table__row-content"
                )
                publisher_links = content_div.find_all(
                    "a", href=lambda x: x and "publishers=" in x
                )
                game_details.publisher.extend(
                    [link.text.strip() for link in publisher_links]
                )

            elif label and "Works on:" in label.text:
                content_div = row.find(
                    "div", class_="details__content table__row-content"
                )
                platforms_text = content_div.text.strip().lower()

                if "windows" in platforms_text:
                    game_details.platforms.append(SupportedOSSystems.WINDOWS.value)
                if "linux" in platforms_text:
                    game_details.platforms.append(SupportedOSSystems.LINUX.value)
                if "mac" in platforms_text:
                    game_details.platforms.append(SupportedOSSystems.MAC.value)

        price_tag = soup.find("span", attrs={"selenium-id": "ProductBasePrice"})
        if price_tag:
            game_details.price = float(price_tag.text.strip().replace("$", ""))
            game_details.is_free = False
        else:
            free_tag = soup.find("span", class_="product-actions-price__final-amount")
            if free_tag and "FREE" in free_tag.text.strip().upper():
                game_details.price = 0.0
                game_details.is_free = True
            else:
                game_details.price = 0.0
                game_details.is_free = False

        return game_details
