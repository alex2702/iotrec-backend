# Generated by Django 2.2.1 on 2019-11-02 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iotrec_api', '0019_remove_recommendation_locality_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stay',
            name='end',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='stay',
            name='last_checkin',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='stay',
            name='start',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
    ]
