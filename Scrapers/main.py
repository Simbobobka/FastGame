import asyncio

from Scrapers.ScraperHandlers.ScraperOrchestrator import ScraperOrchestrator
from Scrapers.utils.logger import get_logger

logger = get_logger(__name__)


async def main():
    """Entry point for all scrapers with Redis integration"""

    orchestrator = ScraperOrchestrator()

    try:
        await orchestrator.run_all()
    except Exception:
        logger.critical("Fatal error running orchestrator", exc_info=True)
    finally:
        logger.info("Scraper orchestrator has stopped.")


if __name__ == "__main__":
    asyncio.run(main())
