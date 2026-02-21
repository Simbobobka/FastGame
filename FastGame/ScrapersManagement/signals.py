from django.db.models.signals import post_save
from django.dispatch import receiver

from .models.RawGamesIds import RawGamesIds


@receiver(post_save, sender=RawGamesIds)
def raw_games_ids_saved_handler(sender, instance, created, **kwargs):
    # TODO: add task to run details scraper
    pass
