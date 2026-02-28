from asyncio import sleep
from datetime import datetime

from bs4 import BeautifulSoup
from playwright.async_api import Page

from Scrapers.AbstractScraper import AbstractScraper
from Scrapers.AllKeyShop.Enums.Genres import Genres
from Scrapers.AllKeyShop.QueryParamethers import CatalogQueryParams
from Scrapers.HttpRequestClient import HttpRequestClient
from Scrapers.RedisClient import RedisScraperClient
from Scrapers.ScraperPlayWrightClient import ScraperClient
from Scrapers.settings import ScrapersConfig, get_config
from Scrapers.utils.Enums.SupportedOsSystems import SupportedOSSystems
from Scrapers.utils.GameModel import GameModel


class AllKeyShopScraper(AbstractScraper):
    """AllKeyShop storefront scraper implementation"""

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
        return "https://www.allkeyshop.com/"

    @property
    def scraper_name(self) -> str:
        """Return the scraper's name"""
        return "allkeyshop"

    async def scrape(self, game_id: str = None, page_number: int = 0):
        if game_id:
            return await self.__scrape_game_details(game_id, page_number)
        else:
            await self.__scrape_game_ids()

    async def __scrape_game_details(
        self,
        game_id: str,
        page_number: int,
    ) -> None: ...

    async def __scrape_game_ids(self):
        """Scrape list of games from AllKeyShop homepage"""
        url = self.base_url + "/api/v2-1-250304/vaks.php"
        params = CatalogQueryParams()
        status, content = await self.http_client.get_request(
            url, params=params.model_dump(), json=True
        )

        if status != 200:
            raise Exception(f"Failed to fetch game IDs, status code: {status}")

        pages: int = content.get("pagination").get("total_pages")

        for page_number in range(1, pages + 1):
            if page_number > 1:
                params.pagenum = page_number
                status, content = await self.http_client.get_request(
                    url, params=params.model_dump(), json=True
                )

                if status != 200:
                    raise Exception(f"Failed to fetch game IDs, status code: {status}")

            game_ids_per_page = self.__extract_game_ids(content.get("products"))
            print(
                f"Scraped {len(game_ids_per_page)} game IDs from page {page_number}/{pages}"
            )
            await self.redis_client.save_last_scrape_page(
                self.scraper_name, Genres.SHOOTER.value, page_number
            )

            try:
                await self.send_data(
                    f"{self.config.django_api}/app/scraped-game-ids/",
                    {
                        "game_ids": list(game_ids_per_page),
                        "genre": Genres.SHOOTER.value,
                        "scraper": self.scraper_name,
                        "page": page_number,
                    },
                )
                print(f"Successfully sent data for page {page_number}")
            except Exception as e:
                print(f"Failed to send data for page {page_number}: {e}")
                print("Continuing with next page...")

    def __extract_game_ids(self, products: list[dict]) -> set[str]:
        """Extract game slug IDs from product links."""
        return {product["link"].rstrip("/").rsplit("/", 1)[-1] for product in products}
