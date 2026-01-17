from pydantic import BaseModel


class GameModel(BaseModel):
    name: str = ""
    url: str = ""
    publisher: list[str] = []
    release_date: str = ""
    price: float = 0.0
    is_free: bool = False
    platforms: list[str] = []
