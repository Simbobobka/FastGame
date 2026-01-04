from abc import ABC, abstractmethod


class AbstractScraper(ABC):
    """Base class for all scrapers with common interface"""
    
    @property
    @abstractmethod
    def browser(self):
        """Return the browser instance"""
        pass
    
    @abstractmethod
    async def scrape(self):
        """Main scraping logic - must be implemented by child classes"""
        pass