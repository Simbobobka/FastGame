from pydantic import BaseModel


class GameModel(BaseModel):
    name: str
    url: str
    publisher: list[str]
    release_date: str
    price: float
    is_free: bool
    platforms: list[str]
