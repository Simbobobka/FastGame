from pydantic import BaseModel

from Scrapers.AllKeyShop.Enums.Genres import Genres


class CatalogQueryParams(BaseModel):
    action: str = "CatalogV2"
    currency: str = "USD"
    price_mode: str = "price_card"
    sort_order: str = "desc"
    pagenum: int = 1
    per_page: int = 50
    type: str = "game"
    genres_tags: str = Genres.SHOOTER.value
