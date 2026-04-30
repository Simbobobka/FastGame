import json
import logging
from typing import Any, Dict

from django.db.models import Avg, Count, Max, Min, Q
from django.db.models.functions import ExtractMonth, ExtractYear

from ..models.GameDetails import GameDetails
from ..models.Platform import Platform
from ..models.Publisher import Publisher

logger = logging.getLogger(__name__)


def _get_bi_platform_coverage() -> Dict[str, Any]:
    """
    Platform coverage analytics.

    Returns:
    - Games per platform with market-share percentage
    - Single vs multi-platform game counts
    - Average platforms per game (uses annotate → aggregate, not nested Avg(Count))
    - Chart data for platform distribution bar chart
    """
    try:
        total_games = GameDetails.objects.count()

        platform_coverage = list(
            Platform.objects.annotate(
                game_count=Count("gamedetails", distinct=True),
            )
            .values("name", "game_count")
            .order_by("-game_count")
        )

        for platform in platform_coverage:
            platform["percentage"] = (
                round((platform["game_count"] / total_games * 100), 1)
                if total_games > 0
                else 0
            )

        avg_result = GameDetails.objects.annotate(
            platform_count=Count("platforms", distinct=True)
        ).aggregate(avg_platforms=Avg("platform_count"))
        avg_platforms_per_game = round(avg_result.get("avg_platforms") or 0, 2)

        single_platform_games = (
            GameDetails.objects.annotate(
                platform_count=Count("platforms", distinct=True)
            )
            .filter(platform_count=1)
            .count()
        )

        multi_platform_games = (
            GameDetails.objects.annotate(
                platform_count=Count("platforms", distinct=True)
            )
            .filter(platform_count__gte=2)
            .count()
        )

        platform_chart_data = json.dumps(
            {
                "labels": [p["name"] for p in platform_coverage],
                "datasets": [
                    {
                        "label": "Games",
                        "data": [p["game_count"] for p in platform_coverage],
                        "backgroundColor": "var(--color-primary-500)",
                        "borderRadius": 4,
                    }
                ],
            }
        )

        return {
            "platform_coverage": platform_coverage,
            "total_games": total_games,
            "single_platform_games": single_platform_games,
            "multi_platform_games": multi_platform_games,
            "avg_platforms_per_game": avg_platforms_per_game,
            "platform_chart_data": platform_chart_data,
        }
    except Exception as e:
        logger.error(f"Error calculating platform coverage: {str(e)}", exc_info=True)
        return {}


def _get_bi_prices_by_platform() -> Dict[str, Any]:
    """
    Platform-based pricing analysis.

    Returns:
    - Avg / min / max price per platform (paid games only)
    - Free vs paid game counts per platform
    - Two chart datasets: avg price + free-vs-paid breakdown
    """
    try:
        pricing_by_platform = list(
            Platform.objects.annotate(
                total_games=Count("gamedetails", distinct=True),
                avg_price=Avg(
                    "gamedetails__price",
                    filter=Q(
                        gamedetails__price__isnull=False, gamedetails__is_free=False
                    ),
                ),
                min_price=Min(
                    "gamedetails__price",
                    filter=Q(
                        gamedetails__price__isnull=False, gamedetails__is_free=False
                    ),
                ),
                max_price=Max(
                    "gamedetails__price",
                    filter=Q(
                        gamedetails__price__isnull=False, gamedetails__is_free=False
                    ),
                ),
                free_count=Count(
                    "gamedetails", distinct=True, filter=Q(gamedetails__is_free=True)
                ),
                paid_count=Count(
                    "gamedetails",
                    distinct=True,
                    filter=Q(
                        gamedetails__is_free=False, gamedetails__price__isnull=False
                    ),
                ),
            )
            .values(
                "name",
                "total_games",
                "avg_price",
                "min_price",
                "max_price",
                "free_count",
                "paid_count",
            )
            .order_by("-total_games")
        )

        platform_price_chart_data = json.dumps(
            {
                "labels": [p["name"] for p in pricing_by_platform],
                "datasets": [
                    {
                        "label": "Avg Price ($)",
                        "data": [
                            float(p["avg_price"]) if p["avg_price"] else 0
                            for p in pricing_by_platform
                        ],
                        "backgroundColor": "var(--color-primary-500)",
                        "borderRadius": 4,
                    }
                ],
            }
        )

        free_paid_chart_data = json.dumps(
            {
                "labels": [p["name"] for p in pricing_by_platform],
                "datasets": [
                    {
                        "label": "Free",
                        "data": [p["free_count"] for p in pricing_by_platform],
                        "backgroundColor": "#10b981",
                        "borderRadius": 4,
                    },
                    {
                        "label": "Paid",
                        "data": [p["paid_count"] for p in pricing_by_platform],
                        "backgroundColor": "var(--color-primary-500)",
                        "borderRadius": 4,
                    },
                ],
            }
        )

        return {
            "pricing_by_platform": pricing_by_platform,
            "platform_price_chart_data": platform_price_chart_data,
            "free_paid_chart_data": free_paid_chart_data,
        }
    except Exception as e:
        logger.error(f"Error calculating prices by platform: {str(e)}", exc_info=True)
        return {}


def _get_bi_publisher_analysis() -> Dict[str, Any]:
    """
    Publisher-based analysis.

    Returns:
    - Top 20 publishers by game count
    - Avg price per publisher (paid games only)
    - Free / paid breakdown per publisher
    - Two chart datasets: games count + avg price
    """
    try:
        top_publishers = list(
            Publisher.objects.annotate(
                game_count=Count("gamedetails", distinct=True),
                avg_price=Avg(
                    "gamedetails__price",
                    filter=Q(
                        gamedetails__price__isnull=False, gamedetails__is_free=False
                    ),
                ),
                free_count=Count(
                    "gamedetails", distinct=True, filter=Q(gamedetails__is_free=True)
                ),
                paid_count=Count(
                    "gamedetails",
                    distinct=True,
                    filter=Q(
                        gamedetails__is_free=False, gamedetails__price__isnull=False
                    ),
                ),
            )
            .values("name", "game_count", "avg_price", "free_count", "paid_count")
            .order_by("-game_count")[:20]
        )

        publishers_chart_data = json.dumps(
            {
                "labels": [p["name"] for p in top_publishers],
                "datasets": [
                    {
                        "label": "Games",
                        "data": [p["game_count"] for p in top_publishers],
                        "backgroundColor": "var(--color-primary-500)",
                        "borderRadius": 4,
                    }
                ],
            }
        )

        publisher_price_chart_data = json.dumps(
            {
                "labels": [p["name"] for p in top_publishers],
                "datasets": [
                    {
                        "label": "Avg Price ($)",
                        "data": [
                            float(p["avg_price"]) if p["avg_price"] else 0
                            for p in top_publishers
                        ],
                        "backgroundColor": "#f59e0b",
                        "borderRadius": 4,
                    }
                ],
            }
        )

        return {
            "top_publishers": top_publishers,
            "publishers_chart_data": publishers_chart_data,
            "publisher_price_chart_data": publisher_price_chart_data,
        }
    except Exception as e:
        logger.error(f"Error calculating publisher analysis: {str(e)}", exc_info=True)
        return {}


def _get_bi_release_trends() -> Dict[str, Any]:
    """
    Release date trends analysis.

    Returns:
    - Releases by year (descending — most recent first)
    - Releases by month with human-readable month names
    - Two chart datasets: yearly + monthly
    """
    try:
        releases_by_year = list(
            GameDetails.objects.filter(release_date__isnull=False)
            .annotate(year=ExtractYear("release_date"))
            .values("year")
            .annotate(count=Count("id"))
            .order_by("-year")
        )

        releases_by_month = list(
            GameDetails.objects.filter(release_date__isnull=False)
            .annotate(month=ExtractMonth("release_date"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        month_names = {
            1: "Jan",
            2: "Feb",
            3: "Mar",
            4: "Apr",
            5: "May",
            6: "Jun",
            7: "Jul",
            8: "Aug",
            9: "Sep",
            10: "Oct",
            11: "Nov",
            12: "Dec",
        }
        for month_data in releases_by_month:
            month_data["month_name"] = month_names.get(month_data["month"], "")

        year_chart_data = json.dumps(
            {
                "labels": [str(r["year"]) for r in releases_by_year],
                "datasets": [
                    {
                        "label": "Releases",
                        "data": [r["count"] for r in releases_by_year],
                        "backgroundColor": "var(--color-primary-500)",
                        "borderRadius": 4,
                    }
                ],
            }
        )

        month_chart_data = json.dumps(
            {
                "labels": [m["month_name"] for m in releases_by_month],
                "datasets": [
                    {
                        "label": "Releases",
                        "data": [m["count"] for m in releases_by_month],
                        "backgroundColor": "#06b6d4",
                        "borderRadius": 4,
                    }
                ],
            }
        )

        return {
            "releases_by_year": releases_by_year,
            "releases_by_month": releases_by_month,
            "year_chart_data": year_chart_data,
            "month_chart_data": month_chart_data,
        }
    except Exception as e:
        logger.error(f"Error calculating release trends: {str(e)}", exc_info=True)
        return {}


def get_bi_statistics_data() -> Dict[str, Any]:
    """
    Aggregate all BI analytics sub-sections into a single context dict.

    Each sub-function handles its own exceptions and returns {} on failure,
    so a single broken section never breaks the entire BI tab.

    Sections:
    - Platform coverage & multi-platform insights
    - Pricing analysis by platform
    - Publisher performance metrics
    - Release date trends and seasonality
    """
    try:
        logger.info("Loading BI statistics data")
        return {
            **_get_bi_platform_coverage(),
            **_get_bi_prices_by_platform(),
            **_get_bi_publisher_analysis(),
            **_get_bi_release_trends(),
        }
    except Exception as e:
        logger.error(f"Error collecting BI statistics: {str(e)}", exc_info=True)
        return {"error": "Error loading BI statistics"}
