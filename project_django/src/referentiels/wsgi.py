"""
WSGI config for referentiels project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# from dj_static import Cling
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'referentiels.settings')

# Avoid statics error with gunicorn --bind=0.0.0.0:8000 referentiels.wsgi
# application = Cling(get_wsgi_application())

# With python manage.py runserver
application = get_wsgi_application()
