from typing import List

from pydantic import BaseModel, ConfigDict, Field

from Scrapers.Steam.Enums.Genres import Genres


class SteamQueryParams(BaseModel):

    cc: str = "US"
    l: str = "ukrainian"
    excluded_descriptors: List[int] = Field(default=[1, 2, 3, 4])
    flavor: str = "contenthub_all"
    strFacetFilter: str = '{"type":7,"value":"game"}'
    start: int = 0
    count: int = 50
    sectionuniqueid: int = 13268
    origin: str = "https://store.steampowered.com"
    strContentHubType: str = "category"
    strContentHubCategory: str = Genres.SHOOTER.value

    def to_params(self) -> list[tuple]:
        scalar = self.model_dump(exclude={"excluded_descriptors"})
        repeated = [
            ("rgExcludedContentDescriptors[]", v) for v in self.excluded_descriptors
        ]
        return list(scalar.items()) + repeated
