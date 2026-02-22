from Scrapers.AbstractScraper import AbstractScraper
from Scrapers.HttpRequestClient import HttpRequestClient
from Scrapers.RedisClient import RedisScraperClient
from Scrapers.ScraperPlayWrightClient import ScraperClient


class ScrapersFactory:
    """Factory for creating scraper instances"""

    @staticmethod
    def create_ids_scraper(
        scrapers: list[AbstractScraper],
        redis_client: RedisScraperClient,
        http_client: HttpRequestClient,
    ) -> list[AbstractScraper]:
        """Create scraper instances"""
        result = []

        for scraper in scrapers:
            ids_browser_client = ScraperClient()

            result.append(
                scraper(
                    redis_client=redis_client,
                    browser_client=ids_browser_client,
                    http_client=http_client,
                )
            )

        return result

    @staticmethod
    def create_details_scraper(
        scrapers: list[AbstractScraper],
        redis_client: RedisScraperClient,
        http_client: HttpRequestClient,
    ) -> list[AbstractScraper]:
        """Create scraper instances"""
        result = []

        for scraper in scrapers:
            details_browser_client = ScraperClient(tabs_quantity=5)

            result.append(
                scraper(
                    redis_client=redis_client,
                    browser_client=details_browser_client,
                    http_client=http_client,
                )
            )

        return result
