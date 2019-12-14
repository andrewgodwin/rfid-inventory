import os
from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("PGDATABASE", "listkeeper"),
        "HOST": os.environ.get("PGHOST", ""),
        "USER": os.environ.get("PGUSER", "postgres"),
        "PASSWORD": os.environ.get("PGPASSWORD", "postgres"),
    }
}

ALLOWED_HOSTS = [x.strip() for x in os.environ.get("ALLOWED_HOSTS", "").split(",") if x.strip()]

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
