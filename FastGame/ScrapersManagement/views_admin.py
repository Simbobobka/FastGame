import json

from django.contrib import admin
from django.db.models import Avg, Count, Max, Min, Q
from django.db.models.functions import ExtractYear
from django.template.response import TemplateResponse

from .models.GameDetails import GameDetails
from .models.RawGamesIds import RawGamesIds
from .models.Source import Source


def statistics_view(request):
    price_by_year = list(
        GameDetails.objects.filter(
            release_date__isnull=False,
            is_free=False,
            price__isnull=False,
        )
        .annotate(year=ExtractYear("release_date"))
        .values("year")
        .annotate(
            avg_price=Avg("price"),
            count=Count("id"),
            min_price=Min("price"),
            max_price=Max("price"),
        )
        .order_by("year")
    )

    stats_by_source = list(
        GameDetails.objects.values("source__name", "source__code")
        .annotate(
            total=Count("id"),
            free_count=Count("id", filter=Q(is_free=True)),
            paid_count=Count("id", filter=Q(is_free=False, price__isnull=False)),
            avg_price=Avg("price", filter=Q(is_free=False, price__isnull=False)),
            min_price=Min("price", filter=Q(is_free=False, price__isnull=False)),
            max_price=Max("price", filter=Q(is_free=False, price__isnull=False)),
        )
        .order_by("source__name")
    )

    raw_ids_by_source = list(
        RawGamesIds.objects.values("source__name")
        .annotate(
            total=Count("id"),
            scraped=Count("id", filter=Q(status="SC")),
            failed=Count("id", filter=Q(status="FA")),
            unprocessed=Count("id", filter=Q(status="UN")),
            in_progress=Count("id", filter=Q(status="IP")),
            retry_waiting=Count("id", filter=Q(status="RW")),
        )
        .order_by("source__name")
    )

    total_games = GameDetails.objects.count()
    total_free = GameDetails.objects.filter(is_free=True).count()
    total_paid = GameDetails.objects.filter(is_free=False, price__isnull=False).count()
    total_sources = Source.objects.filter(is_active=True).count()
    total_raw_ids = RawGamesIds.objects.count()
    total_scraped = RawGamesIds.objects.filter(status="SC").count()
    total_failed = RawGamesIds.objects.filter(status="FA").count()

    # Chart: average price by release year (bar)
    price_chart_data = json.dumps(
        {
            "labels": [str(r["year"]) for r in price_by_year],
            "datasets": [
                {
                    "label": "Avg Price ($)",
                    "data": [float(r["avg_price"]) for r in price_by_year],
                    "backgroundColor": "var(--color-primary-500)",
                    "borderRadius": 4,
                },
            ],
        }
    )

    # Chart: total / free / paid games per source (bar, grouped)
    source_chart_data = json.dumps(
        {
            "labels": [r["source__name"] for r in stats_by_source],
            "datasets": [
                {
                    "label": "Total",
                    "data": [r["total"] for r in stats_by_source],
                    "backgroundColor": "var(--color-primary-400)",
                    "borderRadius": 4,
                },
                {
                    "label": "Free",
                    "data": [r["free_count"] for r in stats_by_source],
                    "backgroundColor": "var(--color-primary-200)",
                    "borderRadius": 4,
                },
                {
                    "label": "Paid",
                    "data": [r["paid_count"] for r in stats_by_source],
                    "backgroundColor": "var(--color-primary-600)",
                    "borderRadius": 4,
                },
            ],
        }
    )

    # Chart: scraping progress per source (stacked bar)
    scraping_chart_data = json.dumps(
        {
            "labels": [r["source__name"] for r in raw_ids_by_source],
            "datasets": [
                {
                    "label": "Scraped",
                    "data": [r["scraped"] for r in raw_ids_by_source],
                    "backgroundColor": "var(--color-primary-500)",
                    "borderRadius": 4,
                    "stack": "total",
                },
                {
                    "label": "Failed",
                    "data": [r["failed"] for r in raw_ids_by_source],
                    "backgroundColor": "#ef4444",
                    "borderRadius": 4,
                    "stack": "total",
                },
                {
                    "label": "Unprocessed",
                    "data": [r["unprocessed"] for r in raw_ids_by_source],
                    "backgroundColor": "#d1d5db",
                    "borderRadius": 4,
                    "stack": "total",
                },
            ],
        }
    )

    stacked_options = json.dumps(
        {
            "scales": {
                "x": {"stacked": True},
                "y": {"stacked": True},
            }
        }
    )

    context = {
        **admin.site.each_context(request),
        "title": "Statistics",
        "price_by_year": list(reversed(price_by_year)),
        "stats_by_source": stats_by_source,
        "raw_ids_by_source": raw_ids_by_source,
        "total_games": total_games,
        "total_free": total_free,
        "total_paid": total_paid,
        "total_sources": total_sources,
        "total_raw_ids": total_raw_ids,
        "total_scraped": total_scraped,
        "total_failed": total_failed,
        "price_chart_data": price_chart_data,
        "source_chart_data": source_chart_data,
        "scraping_chart_data": scraping_chart_data,
        "stacked_options": stacked_options,
    }
    return TemplateResponse(request, "admin/statistics.html", context)
