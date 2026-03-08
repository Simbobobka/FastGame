from django.db import models


class Platform(models.Model):
    """Model representing detailed information about a platform"""

    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
