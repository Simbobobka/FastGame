import logging
from typing import Any, Dict

from ScrapersManagement.Services.ReleaseDateClusteringService import (
    ReleaseDateClusteringService,
)

logger = logging.getLogger(__name__)

_DEFAULT_MIN_CLUSTER_SIZE = 20
_DEFAULT_MAX_CLUSTERS = 10


def get_clasterization_statistics_data(
    min_cluster_size: int = _DEFAULT_MIN_CLUSTER_SIZE,
    max_clusters: int = _DEFAULT_MAX_CLUSTERS,
) -> Dict[str, Any]:
    """Run release-date clustering and return a flat context dict for the Clasterization tab."""
    logger.info(
        "Loading clasterization data — min_cluster_size=%d, max_clusters=%d",
        min_cluster_size,
        max_clusters,
    )
    try:
        result = ReleaseDateClusteringService(
            min_cluster_size=min_cluster_size,
            max_clusters=max_clusters,
        ).run()

        return {
            "clusters": result.clusters,
            "total_games_analysed": result.total_games_analysed,
            "total_games_skipped": result.total_games_skipped,
            "year_min": result.year_min,
            "year_max": result.year_max,
            "algorithm": result.algorithm,
            "n_clusters_found": result.n_clusters_found,
            "clustering_error": result.error,
        }

    except Exception as exc:
        logger.error("Failed to load clasterization data: %s", exc, exc_info=True)
        return {
            "clusters": [],
            "total_games_analysed": 0,
            "total_games_skipped": 0,
            "year_min": 0,
            "year_max": 0,
            "algorithm": "N/A",
            "n_clusters_found": 0,
            "clustering_error": str(exc),
        }
