"""
Minimal Django settings for an API-only service.

Intentionally trimmed down: no sessions, no admin, no auth tables. The only
database table this service touches is `business_items`, and that table is
owned by db/init.sql (the Django model is `managed = False`). That means this
service needs NO migrations and will not fight FastAPI over the schema.
"""
# Core
import os
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-key-not-for-production")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["*"]  # Demo only. Restrict in production.

INSTALLED_APPS = [
    # DRF needs the contenttypes/auth apps registered (its request handling
    # references them). They create no tables here — we never migrate or query
    # them — but they must be installed so model classes have an app_label.
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
    "items",
    "todos",
]

STATIC_URL = "static/"

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "items.middleware.ServedByMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Database (shared Postgres) ---------------------------------------------
# DATABASE_URL example: postgresql://portal:portal@db:5432/portal
_db = urlparse(os.getenv("DATABASE_URL", "postgresql://portal:portal@db:5432/portal"))
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": _db.path.lstrip("/"),
        "USER": _db.username,
        "PASSWORD": _db.password,
        "HOST": _db.hostname,
        "PORT": _db.port or 5432,
    }
}

# --- DRF ---------------------------------------------------------------------
REST_FRAMEWORK = {
    # API-only demo: no auth layer here. Real authorization belongs on the
    # backend behind real identity (Entra ID / JWT), see docs.
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    # Lets drf-spectacular auto-generate the OpenAPI schema from the viewsets.
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# --- OpenAPI / Swagger (drf-spectacular) ------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "Business Modernization Portal — Django service",
    "DESCRIPTION": "REST API (DRF). GraphQL is served separately at /graphql.",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# --- CORS (frontend dev servers) --------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True  # Demo only.

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
