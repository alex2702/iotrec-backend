# Generated by Django 2.2.1 on 2019-10-04 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iotrec_api', '0017_auto_20191004_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preference',
            name='id',
            field=models.UUIDField(default=None, editable=False, primary_key=True, serialize=False),
        ),
    ]
