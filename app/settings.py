from pathlib import Path
import secrets, environ, os
from datetime import timedelta, datetime


BASE_DIR = Path(__file__).resolve().parent.parent
CURRENT_DATE = datetime.now().strftime("%Y%m%d")

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY", default="change-me")
DEBUG = env("DEBUG", bool, False)
APP_NAME = env("APP_NAME", default="")
ENDPOINT = env("ENDPOINT", default="http://127.0.0.1:8000")
FRONTEND_ENDPOINT = env("FRONTEND_ENDPOINT", default=ENDPOINT)
ALLOWED_HOSTS = [str(ah).strip() for ah in env("ALLOWED_HOSTS", default="*").split(",")]
INTERNAL_IPS = ALLOWED_HOSTS

CORS_ALLOW_ALL_ORIGINS = env("CORS_ALLOW_ALL_ORIGINS", default=True)
CORS_ALLOW_CREDENTIALS = env("CORS_ALLOW_CREDENTIALS", default=True)
CORS_ALLOWED_ORIGINS = [
    str(ah).strip() for ah in env("CORS_ALLOWED_ORIGINS", default="").split(",")
]
CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

INSTALLED_APPS = [
    # defaults
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "debug_toolbar",
    "django_extensions",
    "django_filters",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    # custom
    "app_accounts",
    "app_notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
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

WSGI_APPLICATION = "app.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": f'django.db.backends.{env("DATABASE_ENGINE", default="postgresql")}',
        "NAME": env("DATABASE_NAME", default=""),
        "USER": env("DATABASE_USER", default=""),
        "PASSWORD": env("DATABASE_PASSWORD", default=""),
        "HOST": env("DATABASE_HOST", default=""),
        "PORT": env("DATABASE_PORT", default=""),
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

LOG_LEVEL = env("LOG_LEVEL", default="INFO")
LOGGING_HANDLERS = [str(h).strip() for h in env("LOGGING_HANDLERS").split(",")]
LOGGING_FILEPATH = env("LOGGING_FILEPATH", default=os.path.join(BASE_DIR, "logs"))
LOGGING_TIMEBASED = env("LOGGING_TIMEBASED", cast=bool, default=True)
if not os.path.exists(LOGGING_FILEPATH):
    try:
        os.mkdir(LOGGING_FILEPATH)
    except OSError as e:
        print(
            f"[{APP_NAME}::initialization] creating path ({LOGGING_FILEPATH}), Exception - {e} ({type(e)})"
        )
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        }
    },
    "formatters": {
        "default": {
            "format": "[%(levelname)s] %(asctime)s :: %(message)s",
        },
        "colored": {
            "()": "colorlog.ColoredFormatter",  # colored output
            # --> %(log_color)s is very important, that's what colors the line
            "format": "%(log_color)s[%(levelname)s] %(asctime)s :: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": LOG_LEVEL,
            "filters": ["require_debug_true"],
            "class": "colorlog.StreamHandler",
            "formatter": "colored",
        },
        "access_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": f"{LOGGING_FILEPATH}/access{f'.{CURRENT_DATE}' if LOGGING_TIMEBASED else ''}.log",
            "formatter": "default",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": f"{LOGGING_FILEPATH}/error{f'.{CURRENT_DATE}' if LOGGING_TIMEBASED else ''}.log",
            "formatter": "default",
        },
    },
    "loggers": {
        "django": {
            "handlers": LOGGING_HANDLERS,
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "django.request": {
            "handlers": LOGGING_HANDLERS,
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django_extensions.management.commands.runserver_plus": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

REST_FRAMEWORK = {
    # Base API policies
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "app_accounts.authentication.SafeJWTAuthentication",
    ],
    # Schema
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    # Generic view behavior
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "app.core.pagination.Pagination",
    # Filtering
    "SEARCH_PARAM": "q",
}

if not DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
        "rest_framework.renderers.JSONRenderer",
    )
else:
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].append(
        "rest_framework.authentication.SessionAuthentication"
    )

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env("ACCESS_TOKEN_LIFETIME", default=5)),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        minutes=env("REFRESH_TOKEN_LIFETIME", default=60 * 24)
    ),
    "RESET_TOKEN_LIFETIME": timedelta(days=env("RESET_TOKEN_LIFETIME", default=7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "OTHER_SIGNING_KEY": env("OTHER_SIGNING_KEY", default=secrets.token_urlsafe()),
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth App Configurations
AUTH_USER_MODEL = "app_accounts.User"
AUTH_PROFILE_MODULE = "accounts.UserProfile"

# AWS, Static and Media Configurations
AWS_STORAGE_ENABLE = env("AWS_STORAGE_ENABLE", default=False)
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="")
AWS_S3_CUSTOM_DOMAIN = (
    f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
)
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
AWS_S3_SIGNATURE_VERSION = "s3v4"

STATIC_LOCATION = "static"
AWS_LOCATION = STATIC_LOCATION
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = (BASE_DIR / STATIC_LOCATION,)
MEDIA_LOCATION = "media"
MEDIA_ROOT = BASE_DIR / MEDIA_LOCATION

if AWS_STORAGE_ENABLE:
    # Static
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/"
    STATICFILES_STORAGE = "app.core.storages.RemoteStaticStorage"
    # Media
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/"
    DEFAULT_FILE_STORAGE = "app.core.storages.RemoteMediaStorage"
else:
    # Static
    STATIC_URL = f"/api/{STATIC_LOCATION}/"
    # Media
    MEDIA_URL = f"/api/{MEDIA_LOCATION}/"
    DEFAULT_FILE_STORAGE = "app.core.storages.LocalMediaStorage"

# Email configurations
EMAIL_ENABLE = env("EMAIL_ENABLE", default=False)
EMAILS_DEFAULT = [
    str(email).strip() for email in env("EMAILS_DEFAULT", default="").split(",")
]
EMAIL_FROM = env("EMAIL_FROM", default=f"no-reply@appname.com")
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_PORT = env("EMAIL_PORT", default="")

# Cache Settings
# in seconds
# => H * M * S
CACHE_FOR_MONTH = 30 * 7 * 24 * 60 * 60
CACHE_FOR_WEEK = 7 * 24 * 60 * 60
CACHE_FOR_DAY = 24 * 60 * 60
CACHE_FOR_12H = 12 * 60 * 60
CACHE_FOR_1H = 1 * 60 * 60
CACHE_FOR_30MIN = 1 * 30 * 60
CACHE_FOR_10MIN = 1 * 10 * 60
CACHE_FOR_5MIN = 1 * 5 * 60
CACHE_FOR_2MIN = 1 * 2 * 60
CACHE_FOR_1MIN = 1 * 1 * 60
CACHE_FILEDIR = env("CACHE_FILEDIR", default=os.path.join(BASE_DIR, ".cache"))
if not os.path.exists(CACHE_FILEDIR):
    try:
        os.mkdir(CACHE_FILEDIR)
    except OSError as e:
        print(
            f"[{APP_NAME}::initialization] creating path ({CACHE_FILEDIR}), Exception - {e} ({type(e)})"
        )
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": CACHE_FILEDIR,
        "TIMEOUT": 60 * 60,
        "OPTIONS": {"MAX_ENTRIES": 1000},
    }
}

# Server Configurations
# Truncate SQL queries to this many characters (None means no truncation)
RUNSERVER_PLUS_PRINT_SQL_TRUNCATE = None
