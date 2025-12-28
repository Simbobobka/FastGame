from playwright.async_api import async_playwright


class ScraperClient:
    async def initiate(self):
        async with async_playwright() as p:
            self.browser = await p.chromium.connect("ws://localhost:3001/")
            
    async def close_connection(self):
        await self.browser.close()