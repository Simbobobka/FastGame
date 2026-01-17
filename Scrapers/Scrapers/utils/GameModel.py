from pydantic import BaseModel, HttpUrl


class GameModel(BaseModel):
    name: str
    url: HttpUrl
    publisher: list[str]
    release_date: str
    price: float
    is_free: bool
    platforms: list[str]
