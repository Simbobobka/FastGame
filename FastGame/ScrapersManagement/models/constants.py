from django.db import models


class SCRAPING_STATUS(models.TextChoices):
    UNPROCESSED = "UN", "Unprocessed"
    RETRY_WAITING = "RW", "Retry waiting"
    IN_PROGRESS = "IP", "In progress"
    SCRAPED = "SC", "Scraped"
    FAILED = "FA", "Failed"
