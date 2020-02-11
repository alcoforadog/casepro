from casepro.settings_common import *  # noqa

ALLOWED_HOSTS = ["localhost", ".localhost"]

DEBUG = True

HOSTNAME = "localhost:8000"

SITE_API_HOST = "http://localhost:8001/"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "casepro",
        "USER": "casepro",
        "PASSWORD": "nyaruka",
        "HOST": "db",
        "PORT": "5432",
        "ATOMIC_REQUESTS": True,
        "OPTIONS": {},
    }
}
