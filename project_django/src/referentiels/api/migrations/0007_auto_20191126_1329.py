# Generated by Django 2.2.7 on 2019-11-26 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_personnel_fonction_exacte'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personnel',
            name='fonction_exacte',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
    ]
