# Generated by Django 2.2.1 on 2019-10-02 17:24

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('iotrec_api', '0008_auto_20191002_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='recommendation',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False),
        ),
    ]
