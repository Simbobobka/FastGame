from datetime import datetime

from bs4 import BeautifulSoup, Tag

from Scrapers.AbstractScraper import AbstractScraper
from Scrapers.AllKeyShop.Enums.Genres import Genres
from Scrapers.AllKeyShop.QueryParamethers import CatalogQueryParams
from Scrapers.HttpRequestClient import HttpRequestClient
from Scrapers.RedisClient import RedisScraperClient
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

    async def scrape(self, game_id: str = None, page_number: int = 0, raw_id: int = 0):
        if game_id:
            return await self.__scrape_game_details(game_id, page_number, raw_id)
        else:
            await self.__scrape_game_ids()

    async def __scrape_game_details(
        self,
        game_id: str,
        page_number: int,
        raw_id: int,
    ) -> None:
        """Scrape detailed information for a single game"""
        url = self.base_url + f"blog/en-us/{game_id}"
        status, content = await self.http_client.get_request(
            url,
            json=False,
        )

        if status != 200:
            raise Exception(
                f"Failed to fetch game details for {game_id}, status code: {status}"
            )

        game_details = self.__extract_game_details(content, url)

        await self.send_data(
            f"{self.config.django_api}/app/game-details/",
            {
                "game_details": game_details.model_dump(),
                "raw_id": raw_id,
                "scraper": self.scraper_name,
            },
        )

    def __extract_game_details(self, html_content: str, url: str) -> GameModel:
        """Extract game details from HTML content"""
        soup = BeautifulSoup(html_content, "html.parser")

        name = self.__extract_name(soup)
        publisher = self.__extract_info_field(soup, "Publisher")
        release_date = self.__extract_release_date(soup)
        platforms = self.__extract_os_platforms()
        price = self.__extract_recommended_price(soup)

        return GameModel(
            name=name,
            url=url,
            publisher=publisher,
            release_date=release_date,
            platforms=platforms,
            price=price,
            is_free=price == 0.0,
        )

    def __extract_name(self, soup: BeautifulSoup) -> str:
        """Extract game name from the h1 span"""
        tag = soup.select_one("h1 span[data-itemprop='name']")
        return tag.get_text(strip=True) if tag else ""

    def __extract_info_field(self, soup: BeautifulSoup, label: str) -> list[str]:
        """Extract all anchor texts from a game-info-table field by label"""
        value_tag = self.__find_info_value_tag(soup, label)
        if not value_tag:
            return []
        return [a.get_text(strip=True) for a in value_tag.find_all("a")]

    def __extract_info_field_text(self, soup: BeautifulSoup, label: str) -> str:
        """Extract plain text from a game-info-table field by label"""
        value_tag = self.__find_info_value_tag(soup, label)
        return value_tag.get_text(strip=True) if value_tag else ""

    def __extract_release_date(self, soup: BeautifulSoup) -> str:
        """Extract and format release date as dd.mm.yyyy"""
        raw = self.__extract_info_field_text(soup, "Release date")
        if not raw:
            return ""
        try:
            return datetime.strptime(raw, "%d %B %Y").strftime("%d.%m.%Y")
        except ValueError:
            return raw

    def __extract_os_platforms(self) -> list[str]:
        """AllKeyShop does not expose OS info — default to Windows"""
        return [SupportedOSSystems.WINDOWS.value]

    def __extract_recommended_price(self, soup: BeautifulSoup) -> float:
        """Extract price from the second 'ALLKEYSHOP RECOMMENDS' offer block"""
        offers = soup.select("a.recomended_offers")
        if len(offers) < 2:
            return 0.0

        recommended_offer = offers[1]
        price_tag = recommended_offer.select_one("div.offers-price")
        if not price_tag:
            return 0.0

        raw = price_tag.get_text(strip=True).replace("$", "").strip()
        try:
            return float(raw)
        except ValueError:
            return 0.0

    def __find_info_value_tag(self, soup: BeautifulSoup, label: str) -> Tag | None:
        """Find the value div next to a game-info-table-label"""
        for label_tag in soup.select(".game-info-table-label"):
            if label_tag.get_text(strip=True) == label:
                return label_tag.find_next_sibling(class_="game-info-table-value")
        return None

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
                    f"{self.config.django_api}/app/post-game-ids",
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
