# FastGame

A system for collecting and analyzing video game data from multiple stores. Scrapers gather game IDs and details from **Steam**, **GOG**, and **AllKeyShop** and send them to a Django backend, which stores everything in PostgreSQL and provides an admin panel with statistics and scraper controls.

## How It Works

```
 Scrapers (asyncio + Playwright)  ──HTTP POST──▶  Django + DRF  ──▶  PostgreSQL
            ▲                                          │
            └──── task queue / control (Redis) ◀───────┘ Celery (worker, beat, Flower)
```

1. The **IDs worker** walks a store's catalog by genre and page and sends game IDs to the backend (`RawGamesIds`).
2. Django enqueues those games in Redis for detail scraping.
3. The **details worker** (concurrent, 5 by default) picks up tasks from the queue, collects game details (name, description, price, release date, platforms, publisher), and sends them to the backend (`GameDetails`).
4. Failures are retried (`details_max_retries` per source). Tasks that still fail go to a dead letter queue and are synced back to the database with a `Failed` status.
5. From the admin panel you can enable or disable scrapers per source, re-queue failed tasks, and view statistics.

## Project Structure

| Path | Description |
|------|-------------|
| `FastGame/` | Django project: the `ScrapersManagement` app (models, API, Celery tasks, admin, statistics) and `UserManagement` |
| `Scrapers/` | Async scrapers for `Steam`, `SteamDB`, `GOG`, and `AllKeyShop`, plus the orchestrator, factory, and Redis/HTTP clients |
| `docker-compose.yml` | Full stack: Postgres, Redis, Django, Celery worker/beat, Flower, Playwright, scrapers |
| `.github/workflows/` | CI: code quality (Ruff + Black) and a check that PRs reference a Linear ticket |

## Tech Stack

- **Backend:** Python 3.13, Django 5.2, Django REST Framework, django-unfold (admin theme)
- **Background jobs:** Celery, django-celery-beat, Flower, Redis
- **Database:** PostgreSQL
- **Scrapers:** Python 3.12, asyncio, aiohttp, Playwright (remote browser in a container), BeautifulSoup, pydantic-settings
- **Analytics:** scikit-learn, numpy

## Features

- Three store scrapers behind a common `AbstractScraper` interface. A new source is a new class registered in `ScraperOrchestrator`.
- REST API for ingesting scraper data: `POST /app/post-game-ids` and `POST /app/game-details`
- Processing statuses for game IDs: `Unprocessed`, `In progress`, `Retry waiting`, `Scraped`, `Failed`
- Per-source, real-time control of the IDs and details scrapers via Redis
- Admin statistics page with general stats, BI views (platform coverage, publishers, releases by year), and release-era clustering using a Gaussian Mixture Model with automatic cluster count selection (Jenks Natural Breaks as a fallback)

## Getting Started

Requires Docker and Docker Compose.

1. Create a `.env` file in the project root. Variables used by `docker-compose.yml`:
   - Postgres: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`
   - Redis: `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_USER`, `REDIS_USER_PASSWORD`, `REDIS_PASSWORD`
   - Optional: `CELERY_BROKER`, `CELERY_BACKEND`
2. Start the stack:

   ```bash
   docker compose up --build
   ```

   Migrations are applied automatically when the `app` service starts.
3. Create an admin user:

   ```bash
   docker compose exec app python manage.py createsuperuser
   ```

### Ports

| Service | Address |
|---------|---------|
| Django (admin, API) | http://localhost:8002 (admin at `/admin/`) |
| Flower (Celery monitoring) | http://localhost:5557 |
| Playwright server | `localhost:3001` |

## Development

- Linting and formatting: `ruff check .` and `black .` (Ruff config lives in `pyproject.toml`). `pre-commit` is also configured.
- Pull requests must include a Linear ticket ID (for example `FG-23`) in the PR title, branch name, or a commit message.
- Main branch: `develop`
