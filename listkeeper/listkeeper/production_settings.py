import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("PGDATABASE", "listkeeper"),
        "HOST": os.environ.get("PGHOST", ""),
        "USER": os.environ.get("PGUSER", "postgres"),
        "PASSWORD": os.environ.get("PGPASSWORD", "postgres"),
    }
}

ALLOWED_HOSTS = [x.strip() for x in os.environ["ALLOWED_HOSTS"].split(",") if x.strip()]

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]
