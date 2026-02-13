from playwright.async_api import async_playwright

from Scrapers.settings import PlaywrightConfig, get_config


class ScraperClient:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.config = get_config(PlaywrightConfig)

    async def initiate(self):
        """Initialize playwright and connect to browser via websocket"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.connect(
            self.config.playwright_ws_endpoint
        )

    async def close_connection(self):
        """Close browser and playwright connections"""
        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()
