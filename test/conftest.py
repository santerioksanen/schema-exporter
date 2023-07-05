import django


def pytest_configure():
    from django.conf import settings

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            "default": {
                "Engine": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        MIDDLEWARE=("django.middleware.common.CommonMiddleware",),
        INSTALLED_APPS=("rest_framework",),
    )

    django.setup()
