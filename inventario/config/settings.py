import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or "solo-para-desarrollo"
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"

ALLOWED_HOSTS = ["*"]

APPEND_SLASH = False

INSTALLED_APPS = [
    "inventory",
]

MIDDLEWARE = [
    "config.middleware.InternalTokenMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

if os.environ.get("DB_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "HOST": os.environ.get("DB_HOST"),
            "PORT": os.environ.get("DB_PORT", "3306"),
            "NAME": os.environ.get("DB_DATABASE"),
            "USER": os.environ.get("DB_USERNAME"),
            "PASSWORD": os.environ.get("DB_PASSWORD"),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

INTERNAL_TOKEN = os.environ.get("INTERNAL_TOKEN", "")
SERVICE_TIMEOUT = 2
CATALOGO_URL = os.environ.get("CATALOGO_URL", "")
NOTIFICACIONES_URL = os.environ.get("NOTIFICACIONES_URL", "")

LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = False
USE_TZ = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simple"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {"django.request": {"level": "ERROR"}},
}
