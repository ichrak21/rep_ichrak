"""
Django settings for referentiels project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import logging
from keycloak import Client as KeycloakClient

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create load CCI keycloak confiugration
LOGGER = logging.getLogger("")

KEYCLOAK_CONFIG = os.path.join(BASE_DIR, 'referentiels', 'keycloak.json')
try:
    KEYCLOAK_CLIENT = KeycloakClient(config_file=KEYCLOAK_CONFIG)

except Exception as e:
    # TODO remove this after keycloak fix
    LOGGER.debug(e)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
# if os.environ.get('DJANGO_DATABASE') == 'prod':
#    DEBUG = False
# else:
#    DEBUG = True


DEBUG = os.getenv('DEBUG', True) == 'True'
# TODO : put False after debug
DEBUG = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '[contactor] %(levelname)s %(asctime)s %(message)s'
        },
    },
    "handlers": {
        "console_debug": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": "DEBUG",
            'filters': ['require_debug_true'],
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            'filters': ['require_debug_false'],
        },
    },
    "loggers": {
        "": {
            "handlers": ["console","console_debug"],
            'propagate': True,
            "level": "DEBUG",
        },
    },
}

ALLOWED_HOSTS = ['*']

ALLOWED_HOSTS_OLD = [
    'referential.chamberlab.net',
    'api.chamberlab.net',
    '192.168.100.250',
    '104.40.192.64',
    '127.0.0.1',
    'localhost',
    'ichrak.com',
    '::1',
]

# Contrôle sur IP pour les accès à l'API
WHITE_LIST_IP = [
    '81.255.90.115',
    '127.0.0.1',
    'localhost',
    'ichrak.com',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_CREDENTIALS = True

CORS_EXPOSE_HEADERS = ['*']

CSRF_COOKIE_HTTPONLY = False


CORS_ORIGIN_WHITELIST = [
  'http://localhost:3000',
  'http://192.168.0.18:3000',
  'http://127.0.0.1:3000',
  'http://104.40.215.113',
  'https://front-referential.chamberlab.net',
  'https://referential.chamberlab.net',
  'http://ichrak.com:3000',
  'http://ichrak.com:3001'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'referentiels.api',
    'referentiels.signature',
    'reversion',
    'widget_tweaks',
    'corsheaders',
    'django.contrib.postgres'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

ROOT_URLCONF = 'referentiels.urls'

TEMPLATES_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + '/api/templates'

TEMPLATES = [

    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [TEMPLATES_PATH],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'referentiels.jinja2.environment'
        },
    },

    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_PATH],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'referentiels.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases


PROJECT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

DATABASES = {
    'ci_runner': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ci_runner_db',
        'USER': 'ci_runner',
    },
    'local_dev': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'referentiel',
        'USER': 'referentiel',
        'PASSWORD': 'referentiel',
        'HOST': 'db',
        'PORT': '5432',
        'SCHEMA': 'refv2',
    },
    'prod': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB_NAME'),
        'USER': os.environ.get('POSTGRES_LOGIN'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_DB_HOST'),
        'PORT': os.environ.get('POSTGRES_DB_PORT'),
        'SCHEMA': os.environ.get('POSTGRES_SCHEMA')
    },

    'development': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB_NAME'),
        'USER': os.environ.get('POSTGRES_LOGIN'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_DB_HOST'),
        'PORT': os.environ.get('POSTGRES_DB_PORT'),
        'SCHEMA': os.environ.get('POSTGRES_SCHEMA')
    },

    # default used for CI pipeline : only in Python compilation test
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_PATH, 'database.sqlite'),
    },

}

# check if env DJANGO
# database, else raise exception
if os.environ.get('DJANGO_DATABASE') == 'prod':
    if not os.environ.get('POSTGRES_DB_HOST'):
        raise ValueError('env POSTGRES_DB_HOST is not set')
    if not os.environ.get('POSTGRES_LOGIN'):
        raise ValueError('env POSTGRES_LOGIN is not set')
    if not os.environ.get('POSTGRES_PASSWORD'):
        raise ValueError('env POSTGRES_PASSWORD is not set')
    if not os.environ.get('POSTGRES_DB_PORT'):
        raise ValueError('env POSTGRES_DB_PORT is not set')
    if not os.environ.get('POSTGRES_DB_NAME'):
        raise ValueError('env POSTGRES_DB_NAME is not set')
    if not os.environ.get('POSTGRES_SCHEMA'):
        raise ValueError('env POSTGRES_SCHEMA is not set')

# Set default database DJANGO_DATABASE is not set
# use export DJANGO_DATABASE='local_dev' pipenv run manage.py runserver / createsuperuser
# for migration use : pipenv run manage.py --database=local_dev migrate
DEFAULT_DATABASE = os.environ.get('DJANGO_DATABASE', 'default')
DATABASES['default'] = DATABASES[DEFAULT_DATABASE]

# Change la base de donnees par defaut pour les tests
# import sys

# if 'test' in sys.argv or 'test_coverage' in sys.argv:  # Covers regular testing and django-coverage
#    DATABASES['default'] = DATABASES['test']

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend'
    ]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

DATE_INPUT_FORMATS = ['%d/%m/%Y']

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

# STATIC_ROOT not for dev
STATIC_ROOT = DEBUG and None or 'staticfiles'
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'files')
MEDIA_URL = '/storage/'
LOGGER.debug(os.path.join(BASE_DIR, 'files'))

# Add cache parameters

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'boot'),
]

if not os.environ.get('DJANGO_REDIRECT_LOGIN'):
    LOGGER.debug('DJANGO_REDIRECT_LOGIN environment variable is required')

redirect_sso = os.environ.get('DJANGO_REDIRECT_SSO')
redirect_login = os.environ.get('DJANGO_REDIRECT_LOGIN')
SESSION_COOKIE_DOMAIN = os.environ.get('DJANGO_SESSION_COOKIE_DOMAIN')
CSRF_COOKIE_DOMAIN = os.environ.get('DJANGO_CSRF_COOKIE_DOMAIN')

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = None
SESSION_TIMEOUT = 1800

SESSION_COOKIE_MAX_SIZE = 4093

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'ccifrance.test@gmail.com'

scope = 'openid email profile'

URL_SENDINBLUE = "https://api.sendinblue.com/v3/contacts"