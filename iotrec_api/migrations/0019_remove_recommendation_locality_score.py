# Generated by Django 2.2.1 on 2019-11-02 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iotrec_api', '0018_auto_20191102_1401'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recommendation',
            name='locality_score',
        ),
    ]
