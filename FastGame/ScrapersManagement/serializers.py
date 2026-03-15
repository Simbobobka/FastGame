from rest_framework import serializers

from ScrapersManagement.models.constants import SCRAPING_STATUS
from ScrapersManagement.models.Source import Source

from .models.GameDetails import GameDetails
from .models.Platform import Platform
from .models.Publisher import Publisher
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


class GamesDetailsSerializer(serializers.Serializer):
    """
    This serializer is used to serialize and deserialize GameDetails instances,
    converting them to and from JSON representations.
    """

    raw_id = serializers.IntegerField(required=True)
    scraper = serializers.CharField(required=True)
    game_details = serializers.DictField(required=True)

    def validate_raw_id(self, value):
        if not RawGamesIds.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "RawGamesIds with this ID does not exist."
            )
        return value

    def validate_scraper(self, value):
        if not Source.objects.filter(name=value).exists():
            raise serializers.ValidationError("Source with this name does not exist.")
        return value

    def create(self, validated_data: dict) -> GameDetails:
        raw_game_id = RawGamesIds.objects.get(id=validated_data["raw_id"])
        source = Source.objects.get(name=validated_data["scraper"])

        game_details_data = validated_data["game_details"]

        publisher_names = game_details_data.get("publisher", [])
        platform_names = game_details_data.get("platforms", [])

        Publisher.objects.bulk_create(
            [Publisher(name=name) for name in publisher_names],
            ignore_conflicts=True,
        )
        publishers = Publisher.objects.filter(name__in=publisher_names)

        Platform.objects.bulk_create(
            [Platform(name=name) for name in platform_names],
            ignore_conflicts=True,
        )
        platforms = Platform.objects.filter(name__in=platform_names)

        game_details = GameDetails.objects.create(
            name=game_details_data["name"],
            description=game_details_data.get("description", ""),
            release_date=game_details_data["release_date"],
            price=game_details_data.get("price"),
            url=game_details_data["url"],
            is_free=game_details_data.get("is_free", False),
            source=source,
            raw_games_ids=raw_game_id,
        )

        game_details.publisher.set(publishers)
        game_details.platforms.set(platforms)

        return game_details
