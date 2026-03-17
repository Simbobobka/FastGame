import math
import re
from asyncio import sleep
from datetime import datetime

from bs4 import BeautifulSoup

from Scrapers.AbstractScraper import AbstractScraper
from Scrapers.HttpRequestClient import HttpRequestClient
from Scrapers.RedisClient import RedisScraperClient
from Scrapers.Scrapers.Steam.Enums.OsNormalization import OS_NORMALIZATION_MAP
from Scrapers.settings import ScrapersConfig, get_config
from Scrapers.Steam.Enums.Genres import Genres
from Scrapers.Steam.QueryParamethers import SteamQueryParams
from Scrapers.utils.GameModel import GameModel


class SteamScraper(AbstractScraper):
    """STEAM storefront scraper implementation"""

    requires_browser: bool = False

    def __init__(
        self,
        redis_client: RedisScraperClient,
        http_client: HttpRequestClient,
    ):
        super().__init__(redis_client, http_client)
        self.config: ScrapersConfig = get_config(ScrapersConfig)

    @property
    def base_url(self) -> str:
        """Return the base URL"""
        return "https://store.steampowered.com/"

    @property
    def scraper_name(self) -> str:
        """Return the scraper's name"""
        return "steam"

    async def scrape(self, game_id: str = None, page_number: int = 0):
        """Main enter point in scraper"""
        if game_id:
            return await self.__scrape_game_details(game_id, page_number)
        else:
            print("Starting STEAM game ID scraping...")
            await self.__scrape_game_ids()

    async def __scrape_game_ids(self):
        """Scrape list of games from STEAM homepage"""

        url = self.base_url + "saleaction/ajaxgetsaledynamicappquery?"
        params = SteamQueryParams()

        status, content = await self.http_client.get_request(
            url, params=params.model_dump(), json=True
        )

        if status != 200:
            raise Exception(f"Failed to fetch game IDs, status code: {status}")

        page_number = 1
        total_pages = 1

        while page_number <= total_pages:
            game_ids_per_page = tuple(content["appids"])

            status, content = await self.http_client.get_request(
                url, params=params.model_dump(by_alias=True), json=True
            )

            if status != 200:
                raise Exception(f"Failed to fetch game IDs, status code: {status}")
            if page_number == 1:
                total_pages = self.__scrape_pages_quantity(content)
                if total_pages == 0:
                    print("No games found for this query.")
                    break

            game_ids_per_page = content.get("appids", [])

            print(
                f"Scraped {len(game_ids_per_page)} game IDs from page {page_number}/{total_pages}"
            )

            try:
                await self.send_data(
                    f"{self.config.django_api}/app/post-game-ids",
                    {
                        "game_ids": list(game_ids_per_page),
                        "genre": Genres.SHOOTER.value,
                        "scraper": self.scraper_name,
                        "page": page_number,
                    },
                )
                print(f"Successfully sent data for page {page_number}")

                await self.redis_client.save_last_scrape_page(
                    self.scraper_name, Genres.SHOOTER.value, page_number
                )
            except Exception as e:
                print(f"Failed to send data for page {page_number}: {e}")
                print("Continuing with next page...")

            page_number += 1
            params.start += 50

            await sleep(1.5)

    async def __scrape_game_details(self, game_id: str, page_number: int) -> None:
        """Scrape game details from Steam game page"""
        url = self.base_url + f"app/{game_id}/"

        status, content = await self.http_client.get_request(url)

        if status != 200:
            raise Exception(
                f"Failed to fetch game details for {game_id}, status code: {status}"
            )

        game_details = self.__extract_game_details(content, url)
        print(game_details)
        await self.send_data(
            f"{self.config.django_api}/app/game-details/",
            {
                "game_details": game_details.model_dump(mode="json"),
                "game_id": game_id,
                "scraper": self.scraper_name,
            },
        )

    def __extract_game_details(self, content: str, url: str) -> GameModel:
        """Extract game details from game page content"""
        soup = BeautifulSoup(content, "html.parser")
        price = self.__extract_price(soup)

        return GameModel(
            name=self.__extract_name(soup),
            url=url,
            publisher=self.__extract_publisher(soup),
            release_date=self.__extract_release_date(soup),
            platforms=self.__extract_os_platforms(soup),
            price=price,
            is_free=price == 0.0,
          return GameModel(
            name=self.__extract_name(soup),
            url=url,
            publisher=self.__extract_publisher(soup),
            release_date=self.__extract_release_date(soup),
            platforms=self.__extract_os_platforms(soup),
            price=price,
            is_free=price == 0.0,
        )

    def __extract_name(self, soup: BeautifulSoup) -> str:
        """Extract game name"""
        tag = soup.find(id="appHubAppName")
        return tag.get_text(strip=True) if tag else ""

    def __extract_publisher(self, soup: BeautifulSoup) -> list[str]:
        """Extract game publishers"""
        label = soup.find(string=re.compile(r"Видавець:|Publisher:"))
        if not label:
            return []
        subtitle_div = label.parent

        summary_div = subtitle_div.find_next_sibling("div", class_="summary column")

        if summary_div:
            publishers = [a.get_text(strip=True) for a in summary_div.find_all("a")]
        return publishers

    def __extract_release_date(self, soup: BeautifulSoup) -> str:
        """Extract and format release date as dd.mm.yyyy"""

        date_div = soup.find("div", class_="date")

        if not date_div:
            return ""

        raw = date_div.get_text(strip=True)

        try:
            return datetime.strptime(raw, "%d %b, %Y").strftime("%Y-%m-%d")

        except ValueError:
            return raw

    def __extract_os_platforms(self, soup: BeautifulSoup) -> list[str]:
        """Extract list of os platforms game"""
        raw = soup.find_all("div", class_="sysreq_tab")
        platforms = []
        if not raw:
            return []
        raw_os = [i.get("data-os").title() for i in raw]
        for os in raw_os:
            normalized_os = OS_NORMALIZATION_MAP.get(os, os)
            platforms.append(normalized_os)
        return platforms

    def __extract_price(self, soup: BeautifulSoup) -> float:
        """Extract prive from metadata"""
        raw = soup.find("meta", itemprop="price")
        if not raw:
            return 0.0
        return float(raw.get("content"))

    def __scrape_pages_quantity(self, content) -> int:
        """Scrape quantity of pages from Steam homepage"""
        return math.ceil(content["match_count"] / 50)
