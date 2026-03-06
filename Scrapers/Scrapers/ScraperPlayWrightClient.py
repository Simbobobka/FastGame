from playwright.async_api import BrowserContext, Page, async_playwright

from Scrapers.settings import PlaywrightConfig, get_config


class ScraperClient:
    def __init__(self, concurrency: int = 1):
        self.playwright = None
        self.browser = None
        self.concurrency = concurrency
        self.config = get_config(PlaywrightConfig)

    async def initiate(self):
        """Initialize playwright and connect to browser via websocket"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.connect(
            self.config.playwright_ws_endpoint
        )
        self.context: BrowserContext = await self.browser.new_context()
        # each page should have own context
        self.pages: list[Page] = [
            await self.context.new_page() for _ in range(self.concurrency)
        ]

    async def close_connection(self):
        """Close browser and playwright connections"""
        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()
