from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional

from django.db.models import Count
from django.db.models.functions import ExtractYear

from ScrapersManagement.models.GameDetails import GameDetails

logger = logging.getLogger(__name__)

try:
    import numpy as np
    from sklearn.mixture import GaussianMixture

    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False
    logger.warning(
        "scikit-learn / numpy not installed — falling back to Jenks Natural Breaks. "
        "Add 'numpy' and 'scikit-learn' to requirements.txt for better results."
    )

_DEFAULT_MAX_CLUSTERS = 10
_DEFAULT_MIN_CLUSTER_SIZE = 20
_EXAMPLE_GAMES_PER_CLUSTER = 5
_MAX_SAMPLES_PER_YEAR = 300
_JENKS_GVF_TARGET = 0.90


@dataclass
class ReleaseCluster:
    index: int
    label: str
    year_start: int
    year_end: int
    game_count: int
    avg_year: float
    example_games: List[str] = field(default_factory=list)


@dataclass
class ClusteringResult:
    clusters: List[ReleaseCluster]
    total_games_analysed: int
    total_games_skipped: int
    year_min: int
    year_max: int
    algorithm: str
    n_clusters_found: int
    error: Optional[str] = None


class ReleaseDateClusteringService:
    """
    Clusters games into natural release eras using release_date.

    Primary:  Gaussian Mixture Model (sklearn) with BIC-based auto component selection.
    Fallback: Jenks Natural Breaks (pure Python) when sklearn is not available.
    """

    def __init__(
        self,
        max_clusters: int = _DEFAULT_MAX_CLUSTERS,
        min_cluster_size: int = _DEFAULT_MIN_CLUSTER_SIZE,
    ) -> None:
        self.max_clusters = max_clusters
        self.min_cluster_size = min_cluster_size

    def run(self) -> ClusteringResult:
        """Execute the clustering pipeline. Returns a safe ClusteringResult on any error."""
        try:
            return self._run()
        except Exception as exc:
            logger.error("ClusteringService unhandled error: %s", exc, exc_info=True)
            return ClusteringResult(
                clusters=[],
                total_games_analysed=0,
                total_games_skipped=0,
                year_min=0,
                year_max=0,
                algorithm="N/A",
                n_clusters_found=0,
                error=str(exc),
            )

    def _run(self) -> ClusteringResult:
        histogram = self._fetch_histogram()

        if len(histogram) < 2:
            return ClusteringResult(
                clusters=[],
                total_games_analysed=0,
                total_games_skipped=0,
                year_min=0,
                year_max=0,
                algorithm="N/A",
                n_clusters_found=0,
                error="Not enough data — need games released in at least 2 different years.",
            )

        total_with_date = sum(histogram.values())
        total_all = GameDetails.objects.count()
        year_min, year_max = min(histogram), max(histogram)

        if _SKLEARN_AVAILABLE:
            ranges, algorithm = self._gmm_cluster(histogram)
        else:
            ranges, algorithm = self._jenks_cluster(histogram)

        ranges = self._merge_small(ranges, histogram)
        clusters = self._enrich(ranges, histogram)

        return ClusteringResult(
            clusters=clusters,
            total_games_analysed=total_with_date,
            total_games_skipped=total_all - total_with_date,
            year_min=year_min,
            year_max=year_max,
            algorithm=algorithm,
            n_clusters_found=len(clusters),
        )

    def _fetch_histogram(self) -> dict[int, int]:
        """Single GROUP BY query — returns {year: game_count} for all games with a release date."""
        rows = (
            GameDetails.objects.filter(release_date__isnull=False)
            .annotate(year=ExtractYear("release_date"))
            .values("year")
            .annotate(count=Count("id"))
            .order_by("year")
        )
        return {int(r["year"]): int(r["count"]) for r in rows}

    def _gmm_cluster(
        self, histogram: dict[int, int]
    ) -> tuple[list[tuple[int, int]], str]:
        """
        Fit a Gaussian Mixture Model for n_components in [2, max_clusters].
        The optimal n is chosen by BIC (lower = better fit, less risk of overfitting).
        Returns contiguous (year_start, year_end) ranges and an algorithm description string.
        """
        years = sorted(histogram)
        scale = min(1.0, _MAX_SAMPLES_PER_YEAR / max(histogram.values()))

        samples: list[float] = []
        for y in years:
            samples.extend([float(y)] * max(1, int(round(histogram[y] * scale))))
        X = np.array(samples).reshape(-1, 1)

        best_n, best_bic = 2, float("inf")
        max_k = min(self.max_clusters, len(years))

        for n in range(2, max_k + 1):
            try:
                gmm = GaussianMixture(
                    n_components=n,
                    covariance_type="full",
                    random_state=42,
                    max_iter=300,
                    n_init=5,
                )
                gmm.fit(X)
                bic = gmm.bic(X)
                logger.debug("GMM n=%d  BIC=%.1f", n, bic)
                if bic < best_bic:
                    best_bic, best_n = bic, n
            except Exception as exc:
                logger.debug("GMM n=%d failed: %s", n, exc)
                break

        logger.info("GMM BIC selected n_components=%d", best_n)

        final = GaussianMixture(
            n_components=best_n,
            covariance_type="full",
            random_state=42,
            max_iter=500,
            n_init=10,
        )
        final.fit(X)

        means = final.means_.flatten()
        rank = {int(c): i for i, c in enumerate(np.argsort(means))}

        year_arr = np.array(years, dtype=float).reshape(-1, 1)
        labels = final.predict(year_arr)
        year_to_rank = {y: rank[int(lbl)] for y, lbl in zip(years, labels, strict=True)}

        try:
            import sklearn

            version = sklearn.__version__
        except Exception:
            version = "?"

        return self._labels_to_ranges(year_to_rank), (
            f"Gaussian Mixture Model — BIC auto-selected {best_n} components "
            f"(scikit-learn {version})"
        )

    @staticmethod
    def _labels_to_ranges(year_to_rank: dict[int, int]) -> list[tuple[int, int]]:
        """
        Convert {year: cluster_rank} into contiguous (year_start, year_end) tuples.
        A new segment is opened whenever the cluster label changes between adjacent years.
        """
        if not year_to_rank:
            return []

        sorted_years = sorted(year_to_rank)
        segments: list[tuple[int, int]] = []
        seg_start = sorted_years[0]
        prev_year = sorted_years[0]
        prev_rank = year_to_rank[sorted_years[0]]

        for y in sorted_years[1:]:
            cur_rank = year_to_rank[y]
            if cur_rank != prev_rank:
                segments.append((seg_start, prev_year))
                seg_start = y
            prev_year = y
            prev_rank = cur_rank

        segments.append((seg_start, sorted_years[-1]))
        return segments

    def _jenks_cluster(
        self, histogram: dict[int, int]
    ) -> tuple[list[tuple[int, int]], str]:
        """
        Pure-Python fallback. Iterates k from 2 to max_clusters and picks the k
        that first reaches GVF >= _JENKS_GVF_TARGET (goodness-of-variance-fit).
        """
        data: list[float] = []
        for y in sorted(histogram):
            data.extend([float(y)] * min(histogram[y], 100))
        data.sort()

        mean = sum(data) / len(data)
        sdam = sum((x - mean) ** 2 for x in data)
        if sdam == 0:
            years = sorted(histogram)
            return [(years[0], years[-1])], "Jenks Natural Breaks (uniform data)"

        best_k, best_breaks = 2, []
        for k in range(2, min(self.max_clusters, len(histogram)) + 1):
            breaks = _jenks_breaks(data, k)
            gvf = (sdam - _jenks_sdcm(data, breaks)) / sdam
            logger.debug("Jenks k=%d  GVF=%.3f", k, gvf)
            best_k, best_breaks = k, breaks
            if gvf >= _JENKS_GVF_TARGET:
                break

        years = sorted(histogram)
        ranges: list[tuple[int, int]] = []
        for i in range(len(best_breaks) - 1):
            lo = max(int(best_breaks[i]), years[0])
            hi = min(int(best_breaks[i + 1]) - 1, years[-1])
            if lo <= hi:
                ranges.append((lo, hi))

        return (
            ranges or [(years[0], years[-1])],
            f"Jenks Natural Breaks k={best_k} (pure Python)",
        )

    def _merge_small(
        self, ranges: list[tuple[int, int]], histogram: dict[int, int]
    ) -> list[tuple[int, int]]:
        """Merge any era whose game count is below min_cluster_size into its nearest neighbour."""
        changed = True
        while changed and len(ranges) > 1:
            changed = False
            new: list[tuple[int, int]] = []
            i = 0
            while i < len(ranges):
                s, e = ranges[i]
                count = sum(histogram.get(y, 0) for y in range(s, e + 1))
                if count < self.min_cluster_size:
                    if i > 0:
                        ps, pe = new[-1]
                        new[-1] = (ps, e)
                    elif i + 1 < len(ranges):
                        ns, ne = ranges[i + 1]
                        ranges[i + 1] = (s, ne)
                        i += 1
                        continue
                    changed = True
                else:
                    new.append((s, e))
                i += 1
            ranges = new
        return ranges

    def _enrich(
        self, ranges: list[tuple[int, int]], histogram: dict[int, int]
    ) -> list[ReleaseCluster]:
        """Build ReleaseCluster objects: compute weighted avg year, fetch example titles per era."""
        clusters: list[ReleaseCluster] = []
        for idx, (y_start, y_end) in enumerate(sorted(ranges)):
            game_count = sum(histogram.get(y, 0) for y in range(y_start, y_end + 1))
            total_w = sum(histogram.get(y, 0) * y for y in range(y_start, y_end + 1))
            avg_year = round(total_w / game_count, 1) if game_count else float(y_start)

            example_games = list(
                GameDetails.objects.filter(
                    release_date__year__gte=y_start, release_date__year__lte=y_end
                )
                .exclude(name="")
                .order_by("-updated_at")
                .values_list("name", flat=True)[:_EXAMPLE_GAMES_PER_CLUSTER]
            )

            clusters.append(
                ReleaseCluster(
                    index=idx,
                    label=_auto_label(idx, y_start, y_end),
                    year_start=y_start,
                    year_end=y_end,
                    game_count=game_count,
                    avg_year=avg_year,
                    example_games=example_games,
                )
            )
        return clusters


def _jenks_breaks(data: list[float], k: int) -> list[float]:
    """Fisher-Jenks dynamic-programming break computation for k classes."""
    n = len(data)
    mat1 = [[0] * (k + 1) for _ in range(n + 1)]
    mat2 = [[float("inf")] * (k + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        mat2[i][1] = 0.0

    for lst in range(2, n + 1):
        s1 = s2 = w = v = 0.0
        for m in range(1, lst + 1):
            i3 = lst - m + 1
            val = data[i3 - 1]
            s2 += val * val
            s1 += val
            w += 1
            v = s2 - (s1 * s1) / w
            i4 = i3 - 1
            if i4 != 0:
                for j in range(2, k + 1):
                    if mat2[lst][j] >= v + mat2[i4][j - 1]:
                        mat1[lst][j] = i3
                        mat2[lst][j] = v + mat2[i4][j - 1]
        mat1[lst][1] = 1
        mat2[lst][1] = v

    kclass = [0] * (k + 1)
    kclass[k] = n
    for i in range(k, 1, -1):
        kclass[i - 1] = mat1[kclass[i]][i] - 1

    breaks: list[float] = [data[0]]
    for i in range(1, k):
        breaks.append(data[kclass[i]])
    breaks.append(data[-1] + 1)
    return sorted(set(breaks))


def _jenks_sdcm(data: list[float], breaks: list[float]) -> float:
    """Sum of squared deviations from class means — lower means a better classification."""
    sdcm = 0.0
    for i in range(len(breaks) - 1):
        cls = [x for x in data if breaks[i] <= x < breaks[i + 1]]
        if cls:
            mean = sum(cls) / len(cls)
            sdcm += sum((x - mean) ** 2 for x in cls)
    return sdcm


_ERA_MAP = [
    (1970, 1984, "Early Arcade Era"),
    (1985, 1992, "8-Bit / 16-Bit Era"),
    (1993, 1999, "3D Pioneer Era"),
    (2000, 2006, "Online Gaming Dawn"),
    (2007, 2012, "HD Console Era"),
    (2013, 2016, "Early Indie Explosion"),
    (2017, 2020, "Battle Royale & Live-Service Era"),
    (2021, 2024, "Post-Pandemic Digital Era"),
    (2025, 2030, "AI-Assisted Game Dev Era"),
]


def _auto_label(index: int, y_start: int, y_end: int) -> str:
    """Map a year range to the nearest known industry era label from _ERA_MAP."""
    if y_end - y_start > 10:
        return f"Release Wave #{index + 1} ({y_start}–{y_end})"
    mid = (y_start + y_end) / 2
    best_label, best_dist = f"Release Wave #{index + 1}", float("inf")
    for es, ee, lbl in _ERA_MAP:
        dist = abs(mid - (es + ee) / 2)
        if dist < best_dist:
            best_dist, best_label = dist, lbl
    return best_label
