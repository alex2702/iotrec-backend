# Generated by Django 2.2.1 on 2019-10-02 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iotrec_api', '0005_auto_20191002_1647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='created_at',
            field=models.DateTimeField(editable=False),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='updated_at',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='recommendation',
            name='created_at',
            field=models.DateTimeField(editable=False),
        ),
        migrations.AlterField(
            model_name='recommendation',
            name='updated_at',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='thing',
            name='created_at',
            field=models.DateTimeField(editable=False),
        ),
        migrations.AlterField(
            model_name='thing',
            name='updated_at',
            field=models.DateTimeField(),
        ),
    ]
