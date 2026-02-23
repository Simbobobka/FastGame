from rest_framework import serializers

from .models.RawGamesIds import RawGamesIds


class RawGamesIdsSerializer(serializers.ModelSerializer):
    """
    This serializer is used to serialize and deserialize RawGamesIds instances,
    converting them to and from JSON representations.
    """

    class Meta:
        model = RawGamesIds
        fields = [
            "source",
            "game_id",
            "genre",
            "status",
            "page",
            "retry_count",
            "created_at",
            "updated_at",
        ]
