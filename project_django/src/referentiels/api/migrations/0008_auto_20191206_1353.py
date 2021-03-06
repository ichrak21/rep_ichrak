# Generated by Django 3.0 on 2019-12-06 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20191126_1329'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='personnel',
            index=models.Index(fields=['prenom'], name='personnels_prenom'),
        ),
        migrations.AddIndex(
            model_name='personnel',
            index=models.Index(fields=['nom'], name='personnels_nom'),
        ),
        migrations.AddIndex(
            model_name='personnel',
            index=models.Index(fields=['email'], name='personnels_email'),
        ),
        migrations.AddIndex(
            model_name='personnel',
            index=models.Index(fields=['phone'], name='personnels_phone'),
        ),
        migrations.AddIndex(
            model_name='personnel',
            index=models.Index(fields=['fonction_exacte'], name='personnels_fonction_exacte'),
        ),
        migrations.AddIndex(
            model_name='personnel',
            index=models.Index(fields=['matricule'], name='personnels_matricule'),
        ),
        migrations.AddIndex(
            model_name='personnel',
            index=models.Index(fields=['raison_sociale'], name='personnels_raison_sociale'),
        ),
    ]
