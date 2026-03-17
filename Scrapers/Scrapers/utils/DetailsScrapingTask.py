from pydantic import BaseModel


class DetailsScrapingTask(BaseModel):
    game_id: str
    raw_id: int
    scraper_name: str
    genre: str
    attempt: int = 0
    max_retries: int = 3
    error: str = ""
