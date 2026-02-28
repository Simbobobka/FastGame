from typing import Type

from Scrapers.AbstractScraper import AbstractScraper
from Scrapers.HttpRequestClient import HttpRequestClient
from Scrapers.RedisClient import RedisScraperClient
from Scrapers.ScraperHandlers.DetailScraperWorker import DetailScraperWorker
from Scrapers.ScraperHandlers.IdsScraperWorker import IdsScraperWorker
from Scrapers.ScraperHandlers.ScraperWorkerPair import ScraperWorkerPair
from Scrapers.ScraperPlayWrightClient import ScraperClient
from Scrapers.settings import ScrapersConfig, get_config


class ScrapersFactory:
    """Factory for creating scraper instances and workers"""

    def __init__(
        self,
        redis_client: RedisScraperClient,
        http_client: HttpRequestClient,
    ):
        self.redis_client = redis_client
        self.http_client = http_client
        self.config: ScrapersConfig = get_config(ScrapersConfig)

    def create_workers_for_scraper(
        self,
        scraper_class: Type[AbstractScraper],
    ) -> ScraperWorkerPair:
        """Create ID and detail workers for a single scraper class"""
        ids_scraper = self._create_scraper(scraper_class, tabs_quantity=1)
        details_scraper = self._create_scraper(
            scraper_class, tabs_quantity=self.config.tabs_quantity
        )

        return ScraperWorkerPair(
            ids_worker=IdsScraperWorker(scraper=ids_scraper),
            details_worker=DetailScraperWorker(scraper=details_scraper),
        )

    def create_all_workers(
        self,
        scraper_classes: list[Type[AbstractScraper]],
    ) -> list[IdsScraperWorker | DetailScraperWorker]:
        """Create workers for multiple scraper classes"""
        workers = []

        for scraper_class in scraper_classes:
            pair = self.create_workers_for_scraper(scraper_class)
            workers.append(pair.ids_worker)
            workers.append(pair.details_worker)

        return workers

    def _create_scraper(
        self,
        scraper_class: Type[AbstractScraper],
        tabs_quantity: int,
    ) -> AbstractScraper:
        """Create a configured scraper instance"""
        if not scraper_class.requires_browser:
            return scraper_class(
                redis_client=self.redis_client,
                http_client=self.http_client,
            )

        browser_client = ScraperClient(tabs_quantity=tabs_quantity)

        return scraper_class(
            redis_client=self.redis_client,
            http_client=self.http_client,
            browser_client=browser_client,
        )
