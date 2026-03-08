from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models.RawGamesIds import RawGamesIds
from .serializers import GamesDetailsSerializer, RawGamesIdsSerializer


class PostRawGamesIdsAPIView(APIView):
    """API view for bulk creating raw game IDs."""

    def post(self, request):
        serializer = RawGamesIdsSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({"message": "Games processed"}, status=status.HTTP_201_CREATED)


class PostGameDetailsAPIView(APIView):
    """API view for creating game details."""

    def post(self, request):
        serializer = GamesDetailsSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(
            {"message": "Games details processed"}, status=status.HTTP_200_OK
        )
