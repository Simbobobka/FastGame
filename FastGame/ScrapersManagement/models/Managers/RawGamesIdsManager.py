from django.db import models

from ScrapersManagement.signals import post_bulk_create


class RawGamesIdsManager(models.Manager):
    def bulk_create(self, objs, **kwargs):
        created_objs = super().bulk_create(objs, **kwargs)

        post_bulk_create.send(
            sender=self.model,
            instances=created_objs,
        )

        return created_objs
