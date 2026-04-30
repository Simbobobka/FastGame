from . import (
    HomeView,
    StatisticsView,
)  # noqa: F401 — required by admin/__init__.py URL registration
from .bi_statistics import get_bi_statistics_data  # noqa: F401
from .clasterization_statistics import get_clasterization_statistics_data  # noqa: F401
from .general_statistics import get_general_statistics_data  # noqa: F401
