from playwright.async_api import BrowserContext, Page, async_playwright


class ScraperClient:
    def __init__(self, tabs_quantity):
        self.playwright = None
        self.browser = None
        self.tabs_quantity = tabs_quantity

    async def initiate(self):
        """Initialize playwright and connect to browser via websocket"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
        )
        self.contexts: list[Page] = [
            await self.browser.new_context() for _ in range(self.tabs_quantity)
        ]
        # each page should have own context
        self.pages: list[BrowserContext] = [
            await context.new_page() for context in self.contexts
        ]

    async def close_connection(self):
        """Close browser and playwright connections"""
        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()
