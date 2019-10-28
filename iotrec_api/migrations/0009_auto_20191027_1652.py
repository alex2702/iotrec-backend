# Generated by Django 2.2.1 on 2019-10-27 16:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iotrec_api', '0008_auto_20191024_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='improvements',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='rating',
            name='value',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)]),
        ),
    ]