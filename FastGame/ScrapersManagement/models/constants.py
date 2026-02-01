from django.db import models


class SCRAPING_STATUS(models.TextChoices):
    UNPROCESSED = "UN", "Unprocessed"
    SCRAPED = "SC", "Scraped"
    FAILED = "FA", "Failed"
