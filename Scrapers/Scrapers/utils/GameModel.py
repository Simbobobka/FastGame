from pydantic import BaseModel, HttpUrl


class GameModel(BaseModel):
    name: str = ""
    url: HttpUrl | None = None
    publisher: list[str] = []
    release_date: str = ""
    price: float = 0.0
    is_free: bool = False
    platforms: list[str] = []
