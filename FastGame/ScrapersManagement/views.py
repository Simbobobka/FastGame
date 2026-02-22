import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models.RawGamesIds import RawGamesIds
from .models.Source import Source
from .serializers import RawGamesIdsSerializer


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


class PostRawGamesIdsAPIView(APIView):

    def post(self, request):
        serializer = RawGamesIdsSerializer(data=request.data, many=True)
        if serializer.is_valid():
            clean_data = serializer.validated_data

            instances = [RawGamesIds(**item) for item in clean_data]

            RawGamesIds.objects.bulk_create(instances, ignore_conflicts=True)
            return Response(
                {"message": "Games processed"}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
