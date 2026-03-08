from django.db import models

from .Platform import Platform
from .Publisher import Publisher
from .RawGamesIds import RawGamesIds, Source


class GameDetails(models.Model):
    """Model representing detailed information about a game"""

    name = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField(null=False, blank=False)
    price = models.FloatField(null=True, blank=True)
    url = models.URLField(null=False, blank=False)
    is_free = models.BooleanField(default=False)

    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    platforms = models.ManyToManyField(Platform)
    publisher = models.ManyToManyField(Publisher)
    raw_games_ids = models.ForeignKey(RawGamesIds, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
