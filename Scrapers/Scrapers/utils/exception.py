class ScraperError(Exception):
    """Custom exception for scaper's error"""

    def __init__(self, scraper: str, message=None):
        self.scraper = scraper
        self.message = (
            message or f"Scraper {scraper} structure changed: tags need update"
        )
        super().__init__(self.message)
