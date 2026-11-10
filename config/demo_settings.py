"""Settings for the isolated, read-only portfolio demonstration.

Never use a production database or a production secret with this configuration.
"""
from .settings import *  # noqa: F403,F401

DEMO_MODE = True
DEMO_USERNAME = "visitante-demo"
# Deliberately ignore POSTGRES_* and all database URLs.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "demo-data" / "demo.sqlite3",
        "OPTIONS": {"timeout": 20},
    }
}
SESSION_COOKIE_NAME = "savannah_demo_sessionid"
CSRF_COOKIE_NAME = "savannah_demo_csrftoken"
SESSION_COOKIE_AGE = 3600
EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
MIDDLEWARE = list(MIDDLEWARE)
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.contrib.auth.middleware.AuthenticationMiddleware") + 1,
    "core.demo.ReadOnlyDemoMiddleware",
)
