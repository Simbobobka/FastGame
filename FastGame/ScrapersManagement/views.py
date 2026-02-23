from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models.RawGamesIds import RawGamesIds
from .serializers import RawGamesIdsSerializer


class PostRawGamesIdsAPIView(APIView):
    """API view for bulk creating raw game IDs."""

    def post(self, request):
        serializer = RawGamesIdsSerializer(data=request.data, many=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        clean_data = serializer.validated_data

        instances = [RawGamesIds(**item) for item in clean_data]

        RawGamesIds.objects.bulk_create(instances, ignore_conflicts=True)
        return Response({"message": "Games processed"}, status=status.HTTP_201_CREATED)
