import asyncio

from Scrapers.ScraperHandlers.ScraperOrchestrator import ScraperOrchestrator


async def main():
    """Entry point for all scrapers with Redis integration"""

    orchestrator = ScraperOrchestrator()

    try:
        await orchestrator.run_all()
    except Exception as e:
        print(f"Error running orchestrator: {e}")
        pass  # TODO: Add proper error handling/logging
    finally:
        print("Scraper orchestrator has stopped.")


if __name__ == "__main__":
    asyncio.run(main())
