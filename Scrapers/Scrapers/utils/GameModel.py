from pydantic import BaseModel, ConfigDict, HttpUrl


class GameModel(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    name: str = ""
    description: str = ""
    url: HttpUrl | None = None
    publisher: list[str] = []
    release_date: str | None = None
    price: float = 0.0
    is_free: bool = False
    platforms: list[str] = []
