from pydantic import BaseModel

from Scrapers.ScraperHandlers.DetailScraperWorker import DetailScraperWorker
from Scrapers.ScraperHandlers.IdsScraperWorker import IdsScraperWorker


class ScraperWorkerPair(BaseModel):
    """Container for a scraper's workers"""

    model_config = {"arbitrary_types_allowed": True}

    ids_worker: IdsScraperWorker
    details_worker: DetailScraperWorker
