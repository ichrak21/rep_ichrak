# Generated by Django 3.0 on 2019-12-16 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signature', '0003_auto_20191216_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signature',
            name='document',
            field=models.ImageField(upload_to='../files/signature/'),
        ),
    ]
