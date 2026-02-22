from django.urls import path

from .views import PostRawGamesIdsAPIView, process_scraped_games_ids

urlpatterns = [
    path(
        "scraped-game-ids/", process_scraped_games_ids, name="process_scraped_game_ids"
    ),
    path("post-game-ids", PostRawGamesIdsAPIView.as_view(), name="post_raw_games_ids"),
]
