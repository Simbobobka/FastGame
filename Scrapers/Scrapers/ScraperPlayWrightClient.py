import os

from playwright.async_api import async_playwright


class ScraperClient:
    def __init__(self):
        self.playwright = None
        self.browser = None

    async def initiate(self):
        """Initialize playwright and connect to browser via websocket"""
        self.playwright = await async_playwright().start()
        ws_endpoint = os.getenv("PLAYWRIGHT_WS_ENDPOINT", "ws://playwright:3000/")
        self.browser = await self.playwright.chromium.connect(ws_endpoint)

    async def close_connection(self):
        """Close browser and playwright connections"""
        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()
