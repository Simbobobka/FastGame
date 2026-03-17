from django.urls import path

from .views import PostGameDetailsAPIView, PostRawGamesIdsAPIView

urlpatterns = [
    path("post-game-ids", PostRawGamesIdsAPIView.as_view(), name="post_raw_games_ids"),
    path("game-details", PostGameDetailsAPIView.as_view(), name="post_game_details"),
]
