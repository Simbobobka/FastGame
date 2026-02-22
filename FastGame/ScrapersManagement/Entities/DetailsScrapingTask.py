from pydantic import BaseModel


class DetailsScrapingTask(BaseModel):
    game_id: str
    raw_id: int
    scraper_name: str
    genre: str
