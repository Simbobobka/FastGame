from django.db import models

from .constants import SCRAPING_STATUS
from .Source import Source


class RawGamesIds(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    game_id = models.CharField(max_length=50)
    genre = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=SCRAPING_STATUS.choices, db_index=True)
    page = models.IntegerField(null=True)
    retry_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
