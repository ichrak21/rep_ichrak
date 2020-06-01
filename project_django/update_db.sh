#!/usr/bin/env bash

cd /app/src && \
echo -e "Ensure database schema, table are updated" &&\
DJANGO_DATABASE=prod_forced python manage.py migrate &&\
DJANGO_DATABASE=prod_forced python manage.py makemigrations &&\
DJANGO_DATABASE=prod_forced python manage.py migrate &&\

echo -e "Updating database with csv/excel files" &&\
echo -e "Update 'Pays' " &&\
DJANGO_DATABASE=prod_forced python manage.py charger Pays &&\

echo -e "Update 'Region' " &&\
DJANGO_DATABASE=prod_forced python manage.py charger Region &&\

echo -e "Update 'Departement' " &&\
DJANGO_DATABASE=prod_forced python manage.py charger Departement &&\

echo -e "Update 'Qualite' " &&\
DJANGO_DATABASE=prod_forced python manage.py charger Qualite &&\

echo -e "Update 'CCI' " &&\
DJANGO_DATABASE=prod_forced python manage.py charger CCI &&\

echo -e "Update 'CFE' " &&\
DJANGO_DATABASE=prod_forced python manage.py charger CFE &&\

echo -e "Update 'Commune'" &&\
DJANGO_DATABASE=prod_forced pipenv run python manage.py charger Commune &&\

echo -e "Update 'CodePostal'" &&\
DJANGO_DATABASE=prod_forced pipenv run python manage.py charger CodePostal &&\

echo -e "Update 'CFE' (pour la correspondance avec les communes " &&\
DJANGO_DATABASE=prod_forced python manage.py charger CFE 
