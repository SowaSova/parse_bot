import copy
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG") == "True"

# BOT

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "tight-wahoo-separately.ngrok-free.app",
    "147.45.185.78",
    "213.171.8.116",
]

CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.app",
    "http://147.45.185.78",
    "http://213.171.8.116",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # apps
    "apps.users",
    "apps.bot",
    "apps.broadcast",
    "apps.news",
    "apps.products",
    "apps.lottery",
    "tg_bot",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CELERY_BROKER_URL = os.getenv("REDIS_URL")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL")
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_BROKER_POOL_LIMIT = None

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL"),  # Адрес Redis-сервера и номер базы
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "parse",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


# CBOUND
CBONDSSESSID_1 = os.getenv("CBONDSSESSID_1")
CBONDSSESSID_2 = os.getenv("CBONDSSESSID_2")
CF_CLEARANCE = os.getenv("cf_clearance")
CBONDS_TOKEN1 = os.getenv("CBONDS_TOKEN1")
CBONDS_TOKEN2 = os.getenv("CBONDS_TOKEN2")
CBONDS_USERNAME = os.getenv("CBONDS_USERNAME")
CBONDS_PASSWORD = os.getenv("CBONDS_PASSWORD")
CBONDS_OTP = os.getenv("CBONDS_OTP")

# ADMIN ORDER
ADMIN_ORDERING = [
    ("users", ["TelegramUser"]),
    ("news", ["NewsFilter", "NewsChannel"]),
    ("products", ["Product", "Cart"]),
    ("lottery", ["Lottery"]),
    ("broadcast", ["Broadcast"]),
    ("bot", ["FAQ", "Manager"]),
]


def get_app_list(self, request):
    app_dict = self._build_app_dict(request)

    app_dict_copy = copy.deepcopy(app_dict)
    for app_label, object_list in ADMIN_ORDERING:
        app = app_dict_copy.pop(app_label)
        object_dict = {value: idx for idx, value in enumerate(object_list)}
        app["models"].sort(
            key=lambda x: object_dict.get(x["object_name"], len(object_list) + 1)
        )
        yield app

    app_list = sorted(app_dict_copy.values(), key=lambda x: x["name"].lower())
    for app in app_list:
        app["models"].sort(key=lambda x: x["name"])
        yield app
