"""
Configuracion de Django para el microservicio de Proveedores.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Clave de desarrollo generada por Django (no usar en produccion)
SECRET_KEY = 'django-insecure-rhs!2e!ine)$4c1m1+(uml$ej4#9+p+n*_+xkhny#m3jjnhmdg'

DEBUG = os.environ.get("DEBUG", "False") == "True"

# El Gateway llega con el host "proveedores:8000"
ALLOWED_HOSTS = ["*"]

# El Gateway envia las rutas sin "/" al final
APPEND_SLASH = False


# Aplicaciones

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'suppliers',
]

MIDDLEWARE = [
    'config.middleware.InternalTokenMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Base de datos: se lee de las variables de entorno

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT", "3306"),
        "NAME": os.environ.get("DB_DATABASE"),
        "USER": os.environ.get("DB_USERNAME"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internacionalizacion

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# El Gateway ya autentica al usuario: el servicio no usa sesiones ni usuarios de Django

REST_FRAMEWORK = {
        "EXCEPTION_HANDLER": "suppliers.errors.custom_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}