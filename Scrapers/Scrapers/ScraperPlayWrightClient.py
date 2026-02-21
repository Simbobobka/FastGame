from playwright.async_api import BrowserContext, Page, async_playwright


class ScraperClient:
    def __init__(self, tabs_quantity: int = 1):
        self.playwright = None
        self.browser = None
        self.tabs_quantity = tabs_quantity

    async def initiate(self):
        """Initialize playwright and connect to browser via websocket"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # TODO: connect to docker
        )
        self.context: BrowserContext = await self.browser.new_context()
        # each page should have own context
        self.pages: list[Page] = [
            await self.context.new_page() for _ in range(self.tabs_quantity)
        ]

    async def close_connection(self):
        """Close browser and playwright connections"""
        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()
