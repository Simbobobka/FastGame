from django.db import models


class Source(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True, db_index=True)
    ids_scraper_enabled = models.BooleanField(default=True, db_index=True)
    details_scraper_enabled = models.BooleanField(default=True, db_index=True)
    details_max_retries = models.PositiveSmallIntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
