# PoC chargement de fichier intégré dans Django

PoC pour le chargement de fichier en python

Les fichiers de tests sont placés dans le répertoire fichiers

Le PoC charge dans les tables créées par le framework Django : `api_continent`
et `api_pays`. Le système vide les données. A utiliser uniquement pour
l'initialisation pour le moment.

Pour lancer démarrer dans une premier temps une base de données `docker-compose up -d`

Puis dans un environnement `virtualenv`

```
python manage.py charger Pays
python manage.py charger Region
python manage.py charger Departement
python manage.py charger Commune
```
