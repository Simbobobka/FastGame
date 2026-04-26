from django.urls import reverse_lazy

UNFOLD = {
    "SITE_TITLE": "FastGame",
    "SITE_HEADER": "FastGame APP",
    "SITE_LOGO": "/static/logo.png",
    "SITE_ICON": "/static/logo.png",
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "href": "/static/logo.ico",
            "type": "image/x-icon",
        },
        {
            "rel": "shortcut icon",
            "href": "/static/logo.ico",
            "type": "image/x-icon",
        },
        {
            "rel": "icon",
            "href": "/static/logo.png",
            "type": "image/png",
            "sizes": "32x32",
        },
        {
            "rel": "icon",
            "href": "/static/logo.png",
            "type": "image/png",
            "sizes": "192x192",
        },
        {
            "rel": "apple-touch-icon",
            "href": "/static/logo.png",
            "sizes": "180x180",
        },
    ],
    "COLORS": {
        "primary": {
            "50": "243 244 249",
            "100": "227 229 240",
            "200": "196 201 223",
            "300": "158 165 198",
            "400": "112 120 163",
            "500": "73 82 128",
            "600": "52 58 92",
            "700": "40 42 65",
            "800": "30 32 50",
            "900": "20 22 35",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Scrapers Management",
                "items": [
                    {
                        "title": "Scrapers Management",
                        "icon": "dashboard",
                        "link": reverse_lazy(
                            "admin:app_list",
                            kwargs={"app_label": "ScrapersManagement"},
                        ),
                    },
                    {
                        "title": "Statistics",
                        "icon": "bar_chart",
                        "link": reverse_lazy("admin:statistics"),
                    },
                    {
                        "title": "Game Details",
                        "icon": "sports_esports",
                        "link": reverse_lazy(
                            "admin:ScrapersManagement_gamedetails_changelist"
                        ),
                    },
                    {
                        "title": "Platforms",
                        "icon": "devices",
                        "link": reverse_lazy(
                            "admin:ScrapersManagement_platform_changelist"
                        ),
                    },
                    {
                        "title": "Publishers",
                        "icon": "apartment",
                        "link": reverse_lazy(
                            "admin:ScrapersManagement_publisher_changelist"
                        ),
                    },
                    {
                        "title": "Raw Game IDs",
                        "icon": "tag",
                        "link": reverse_lazy(
                            "admin:ScrapersManagement_rawgamesids_changelist"
                        ),
                    },
                    {
                        "title": "Sources",
                        "icon": "hub",
                        "link": reverse_lazy(
                            "admin:ScrapersManagement_source_changelist"
                        ),
                    },
                ],
            }
        ],
    },
}
