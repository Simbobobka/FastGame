from constants import SCRAPING_STATUS
from django.db import models
from source_model import Source


class RawGamesIds(models.Model):
    source_id = models.ForeignKey(Source, on_delete=models.CASCADE)
    source = models.CharField(max_length=50)
    genre = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=SCRAPING_STATUS.choices)
    page = models.IntegerField(null=True)
    retry_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
