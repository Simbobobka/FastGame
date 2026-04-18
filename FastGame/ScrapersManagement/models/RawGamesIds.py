from django.db import models

from ScrapersManagement.models.Managers.RawGamesIdsManager import RawGamesIdsManager

from .constants import SCRAPING_STATUS
from .Source import Source


class RawGamesIds(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    game_id = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    status = models.CharField(
        max_length=50, choices=SCRAPING_STATUS.choices, db_index=True
    )
    page = models.IntegerField(null=True)
    retry_count = models.IntegerField(default=0)
    last_error = models.TextField(blank=True, default="")
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RawGamesIdsManager()

    def __str__(self) -> str:
        return self.game_id

    class Meta:
        indexes = [
            models.Index(fields=["source", "status"]),
            models.Index(fields=["updated_at"]),
        ]
