from asyncio import sleep
from datetime import datetime

from bs4 import BeautifulSoup
from playwright.async_api import Page

from Scrapers.AbstractScraper import AbstractScraper
from Scrapers.AllKeyShop.Enums.Genres import Genres
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

    async def scrape(self, game_id: str = None, page_number: int = 0): ...
