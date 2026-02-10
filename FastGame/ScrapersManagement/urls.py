from django.urls import path

from .views import process_scraped_games_ids

urlpatterns = [
    path(
        "scraped-game-ids/", process_scraped_games_ids, name="process_scraped_game_ids"
    ),
]
