from abc import ABC, abstractmethod


class AbstractScraper(ABC):
    @property
    @abstractmethod
    def browser(self):
        pass
    
    @abstractmethod
    async def scrape(self):
        pass