from celery import shared_task

from .models.RawGamesIds import RawGamesIds


@shared_task
def run_details_scraper():
    pass
