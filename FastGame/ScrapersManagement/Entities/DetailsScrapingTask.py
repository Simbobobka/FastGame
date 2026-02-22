from pydantic import BaseModel


class DetailsScrapingTask(BaseModel):
    game_id: int
    raw_id: int
    scraper_name: str
    genre: str
