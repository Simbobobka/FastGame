from django.contrib import admin
from django.urls import path

from .GameDetailsAdmin import GameDetailsAdmin
from .PlatformAdmin import PlatformAdmin
from .PublisherAdmin import PublisherAdmin
from .RawGamesIdsAdmin import RawGamesIdsAdmin
from .SourceAdmin import SourceAdmin


def _get_urls(self):
    from ..views_admin import StatisticsView

    return [
        path(
            "statistics/",
            self.admin_view(StatisticsView.statistics_view),
            name="statistics",
        ),
    ] + _original_get_urls(self)


_original_get_urls = admin.site.__class__.get_urls
admin.site.__class__.get_urls = _get_urls
