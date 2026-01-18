import asyncio

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from ..AbstractScraper import AbstractScraper
from ..ScraperPlayWrightClient import ScraperClient
from ..SteamDB.Genres import Genres
from ..utils.exception import ScraperError
from ..utils.Enums.SupportedOsSystems import SupportedOSSystems
from ..utils.GameModel import GameModel


class SteamDBScraper(AbstractScraper):

    def __init__(self):
        """Initialize the scraper with a Playwright client."""
        self.client = ScraperClient()

    @property
    def base_url(self) -> str:
        """Return the full URL"""
        return "https://steamdb.info/"

    @property
    def browser(self):
        """Return the browser instance from the client."""
        return self.client.browser

    async def scrape(self):
        """Scrape app IDs from all pages and detail info about game of the genre."""
        await self.client.initiate()

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
            await self.__scrape_game_ids__()
            await self.__scrape_game_details__("730")
        except AttributeError as e:
            raise ScraperError("SteamDB") from e

        finally:
            await self.client.close_connection()

    async def __scrape_game_ids__(self):
        """Scrape game IDs from all pages"""

        await self.page.goto(
            self.base_url + f"tag/{Genres.SHOOTER.value}/" + "?min_reviews=500"
        )
        content = await self.page.content()
        max_page = await self.__get_number_of_pages__(content)

        ids = []
        for page_num in range(max_page):
            content = await self.page.content()
            ids_current = await self.__extract_ids_per_page__(content)
            ids.extend(ids_current)
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

        return int(buttons[-2].get_text(strip=True)) if len(buttons) >= 2 else 1

    async def __extract_ids_per_page__(self, content):
        """Extract app IDs from the current page's table rows."""

        soup = BeautifulSoup(content, "html.parser")
        rows = soup.select("tr.app[data-appid]")
        if not rows:
            pass
        app_ids = [row.get("data-appid") for row in rows]

        return app_ids

    async def __scrape_game_details__(self, game_id: str) -> GameModel:
        """scrape game details from SteamDB game page"""

        game_url = self.base_url + f"app/{game_id}/"
        await self.page.goto(game_url)
        content = await self.page.content()
        soup = BeautifulSoup(content, "html.parser")
        price_status = self.__check_price_status__(soup)

        return GameModel(
            name=soup.find(attrs={"itemprop": "name"}).get_text(),
            url=game_url,
            publisher=self.__scrape_publishers__(soup),
            release_date=self.__scrape_release_date__(soup),
            platforms=self.__scrape_platforms__(soup),
            **price_status,
        )

    def __check_price_status__(self, soup: BeautifulSoup) -> dict[str, bool | float]:
        """scrape info about price and free status"""
        is_free = False
        price = 0.0

        is_free_row = soup.find("td", string="IsFreeApp")

        if is_free_row:
            is_free = is_free_row.find_next_sibling("td").get_text(strip=True) == "Yes"

        price_tag = soup.select_one('td.price-line[data-cc="us"]+td')

        if price_tag:
            text = price_tag.get_text(strip=True)

            if text != "N/A":
                try:
                    price = float(text)
                    is_free = False if price > 0 else True
                except ValueError:
                    price = 0.0
                    is_free = True

        return {"is_free": is_free, "price": price}

    def __scrape_publishers__(self, soup: BeautifulSoup) -> list[str]:
        """scrape publishers of game"""
        publisher_tags = soup.find_all("a", attrs={"itemprop": "publisher"})

        return [i.get("content") for i in publisher_tags]

    def __scrape_platforms__(self, soup: BeautifulSoup) -> list[str]:
        """scrape platforms"""
        platform_tags = soup.find("meta", attrs={"itemprop": "operatingSystem"})
        raw = platform_tags.get("content")

        platforms = []
        for platform in raw.split(","):
            platform_cleaned = platform.strip()
            if platform_cleaned == "Windows":
                platforms.append(SupportedOSSystems.WINDOWS.value)
            elif platform_cleaned == "macOS":
                platforms.append(SupportedOSSystems.MAC.value)
            elif platform_cleaned == "Linux":
                platforms.append(SupportedOSSystems.LINUX.value)

        return platforms

    def __scrape_release_date__(self, soup: BeautifulSoup) -> str:
        """scrape release date"""
        date_tag = soup.find("relative-time", {"itemprop": "datePublished"})

        return date_tag.get("content")
