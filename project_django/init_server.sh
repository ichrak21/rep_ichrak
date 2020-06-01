#!/usr/bin/env bash

# Start memcached
service memcached start &&\
mkdir -p /app/src/boot &&\

if [ -z "$APP_ENVIRONMENT" ] 
then
	APP_ENVIRONMENT=production
fi
# 
# DJANGO_DATABASE=prod_forced python manage.py makemigrations api &&\
# Start server
cd /app/src &&\
DJANGO_DATABASE=$APP_ENVIRONMENT python manage.py makemigrations &&\
DJANGO_DATABASE=$APP_ENVIRONMENT python manage.py migrate &&\
DJANGO_DATABASE=$APP_ENVIRONMENT python manage.py migrate api &&\
DJANGO_DATABASE=$APP_ENVIRONMENT python manage.py collectstatic --noinput --clear &&\
mkdir -p /docker/backoffice/logs &&\
touch /docker/backoffice/logs/gunicorn.log &&\
touch /docker/backoffice/logs/access.log &&\
DJANGO_DATABASE=$APP_ENVIRONMENT gunicorn referentiels.wsgi -b 0.0.0.0:8000 \
    --bind unix:django_app.sock \
    --workers 5 --timeout 500

# \
#    --log-level debug \
#    --error-logfile "-"
