# Sample local settings file
# Copy this to localsettings.py and edit settings as needed

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False

# list of IPs that are allowed to see debug output in templates
INTERNAL_IPS = []

ALLOWED_HOSTS = []

# SECURITY WARNING: keep the secret key used in production secret!
# You can generate one here: http://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = ']:7=:|]*AEI@+vHN%hQM-Kv_PKFXM:>8J*tiJKI5{kR}#`cO&H'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Exist DB Settings
EXISTDB_SERVER_URL = 'http://localhost:8080/exist/'
# exist admin account for testing
EXISTDB_SERVER_USER = "admin"
EXISTDB_SERVER_PASSWORD = ""
EXISTDB_ROOT_COLLECTION = "/ddi_data"
# a bug in python xmlrpclib loses the timezone; override it here
# most likely, you want either tz.tzlocal() or tz.tzutc()
from dateutil import tz
EXISTDB_SERVER_TIMEZONE = tz.tzlocal()

# geonames username to use when geocoding locations at data-load time
GEONAMES_USERNAME = ''

# Logging
# https://docs.djangoproject.com/en/1.6/topics/logging/
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'basic': {
            'format': '[%(asctime)s] %(levelname)s:%(name)s::%(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'basic'
        },
    },
    'loggers': {
        'ddisearch': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}
