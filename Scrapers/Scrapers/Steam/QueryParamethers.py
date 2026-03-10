from pydantic import BaseModel, Field

from Scrapers.Steam.Enums.Genres import Genres


class SteamQueryParams(BaseModel):
    cc: str = "US"
    l: str = "ukrainian"
    rgExcludedContentDescriptors: list[int] = Field(
        default=[3, 4], alias="rgExcludedContentDescriptors[]"
    )
    flavor: str = "contenthub_all"
    strFacetFilter: str = '{"type":7,"value":"game"}'
    start: int = 0
    count: int = 50
    sectionuniqueid: int = 13268
    origin: str = "https://store.steampowered.com"
    strContentHubType: str = "category"
    strContentHubCategory: str = Genres.SHOOTER.value
