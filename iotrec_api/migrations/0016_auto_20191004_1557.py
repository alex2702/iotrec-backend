# Generated by Django 2.2.1 on 2019-10-04 15:57

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('iotrec_api', '0015_auto_20191004_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preference',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False),
        ),
    ]
