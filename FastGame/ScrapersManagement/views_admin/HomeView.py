from django.db.models import Count, Q
from django.shortcuts import render

from ..models.constants import SCRAPING_STATUS
from ..models.GameDetails import GameDetails
from ..models.RawGamesIds import RawGamesIds
from ..models.Source import Source


def home_view(request):
    total_games = GameDetails.objects.count()
    total_sources = Source.objects.count()
    total_free = GameDetails.objects.filter(is_free=True).count()
    total_scraped = RawGamesIds.objects.filter(status=SCRAPING_STATUS.SCRAPED).count()

    sources = list(
        Source.objects.annotate(
            games_count=Count(
                "rawgamesids",
                filter=Q(rawgamesids__status=SCRAPING_STATUS.SCRAPED),
            )
        ).values("name", "code", "games_count")
    )

    context = {
        "total_games": total_games,
        "total_sources": total_sources,
        "total_free": total_free,
        "total_scraped": total_scraped,
        "sources": sources,
    }

    return render(request, "home.html", context)
