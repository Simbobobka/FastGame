from rest_framework import serializers

from .models.RawGamesIds import RawGamesIds


class RawGamesIdsSerializer(serializers.ModelSerializer):
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
