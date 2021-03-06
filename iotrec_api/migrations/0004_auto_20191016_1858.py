# Generated by Django 2.2.1 on 2019-10-16 18:58

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iotrec_api', '0003_auto_20191014_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='value',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(-1), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='preference',
            name='id',
            field=models.CharField(editable=False, max_length=255, primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.UUIDField(default=None, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('updated_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('value', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('recommendation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iotrec_api.Recommendation')),
            ],
        ),
    ]
