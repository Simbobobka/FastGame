from rest_framework import serializers

from ScrapersManagement.models.constants import SCRAPING_STATUS
from ScrapersManagement.models.Source import Source

from .models.RawGamesIds import RawGamesIds


class RawGamesIdsSerializer(serializers.Serializer):
    """
    This serializer is used to serialize and deserialize RawGamesIds instances,
    converting them to and from JSON representations.
    """

    game_ids = serializers.ListField(child=serializers.CharField(), allow_empty=False)
    genre = serializers.CharField()
    scraper = serializers.CharField()
    page = serializers.IntegerField(required=False, allow_null=True, default=None)

    def create(self, validated_data: dict) -> list[RawGamesIds]:
        source, _ = Source.objects.get_or_create(
            name=validated_data.get("scraper"),
            defaults={"code": validated_data.get("scraper").lower()},
        )

        instances = [
            RawGamesIds(
                source=source,
                game_id=game_id,
                genre=validated_data["genre"],
                status=SCRAPING_STATUS.UNPROCESSED,
                page=validated_data["page"],
            )
            for game_id in validated_data["game_ids"]
        ]

        return RawGamesIds.objects.bulk_create(instances)
