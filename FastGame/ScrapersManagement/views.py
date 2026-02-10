import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models.RawGamesIds import RawGamesIds
from .models.Source import Source


@csrf_exempt
def process_scraped_games_ids(request) -> JsonResponse:
    """Endpoint to process scraped game IDs from Redis stream"""
    if request.method == "POST":
        data = json.loads(request.body)
        game_ids = data.get("game_ids", [])
        genre = data.get("genre")
        scraper = data.get("scraper")
        page = data.get("page")

        source, _ = Source.objects.get_or_create(name=scraper)

        raw_games = [
            RawGamesIds(
                source=source,
                source_name=id,
                genre=genre,
                status="Unprocessed",
                page=page,
            )
            for id in game_ids
        ]
        RawGamesIds.objects.bulk_create(raw_games)

        return JsonResponse({"message": "Received game IDs"}, status=200)

    return JsonResponse({"error": "Method not allowed"}, status=405)
