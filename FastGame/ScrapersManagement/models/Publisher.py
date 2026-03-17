from django.db import models


class Publisher(models.Model):
    """Model representing detailed information about a publisher"""

    name = models.CharField(max_length=255, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
