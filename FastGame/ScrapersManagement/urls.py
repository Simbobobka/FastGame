from django.urls import path

from .views import PostRawGamesIdsAPIView

urlpatterns = [
    path("post-game-ids", PostRawGamesIdsAPIView.as_view(), name="post_raw_games_ids"),
]
