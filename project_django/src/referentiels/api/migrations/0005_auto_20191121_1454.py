# Generated by Django 2.2.7 on 2019-11-21 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20191120_1419'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='personnel',
            name='fonction_exacte',
        ),
        migrations.AlterField(
            model_name='personnel',
            name='date_debut_fonction',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AlterField(
            model_name='personnel',
            name='date_fin_fonction',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
    ]