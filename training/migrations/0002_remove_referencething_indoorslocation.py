# Generated by Django 2.2.1 on 2019-09-18 16:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='referencething',
            name='indoorsLocation',
        ),
    ]