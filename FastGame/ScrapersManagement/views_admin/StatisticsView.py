import logging

from django.contrib import admin
from django.template.response import TemplateResponse

from .bi_statistics import get_bi_statistics_data
from .clasterization_statistics import get_clasterization_statistics_data
from .general_statistics import get_general_statistics_data

logger = logging.getLogger(__name__)


_VALID_TABS = ("general", "bi", "clasterization")


_AVAILABLE_TABS = [
    {"name": "general", "label": "General Statistics", "icon": "summary"},
    {"name": "bi", "label": "BI", "icon": "analytics"},
    {"name": "clasterization", "label": "Clasterization", "icon": "cluster"},
]

_TAB_DATA_HANDLERS = {
    "general": get_general_statistics_data,
    "bi": get_bi_statistics_data,
    "clasterization": get_clasterization_statistics_data,
}


def statistics_view(request) -> TemplateResponse:
    """
    Main Statistics admin view with tab-based navigation.

    URL: /admin/statistics/
    Query params:
        tab (str): One of 'general' | 'bi' | 'clasterization'. Defaults to 'general'.

    Security:
        Wrapped by admin.site.admin_view() in ScrapersManagement/admin/__init__.py,
        which enforces Django admin authentication and CSRF. No extra decorator needed.

    Returns:
        TemplateResponse rendered from admin/statistics.html with full admin context
        plus tab-specific data merged at the top level.
    """
    raw_tab = request.GET.get("tab", "general").lower()
    active_tab = raw_tab if raw_tab in _VALID_TABS else "general"

    if raw_tab not in _VALID_TABS:
        logger.warning(
            "Invalid statistics tab requested: '%s' by user '%s'. Defaulting to 'general'.",
            request.GET.get("tab"),
            request.user.username,
        )

    logger.info(
        "Statistics page accessed — user: %s, tab: %s",
        request.user.username,
        active_tab,
    )

    try:
        tab_data = _TAB_DATA_HANDLERS[active_tab]()
    except Exception as e:
        logger.error(
            "Unhandled error loading '%s' statistics: %s",
            active_tab,
            str(e),
            exc_info=True,
        )
        tab_data = {
            "error": f"Error loading {active_tab} statistics. Check server logs."
        }

    context = {
        **admin.site.each_context(request),
        "title": "Statistics",
        "active_tab": active_tab,
        "available_tabs": _AVAILABLE_TABS,
        **tab_data,
    }

    return TemplateResponse(request, "admin/statistics.html", context)
