# Generated by Django 2.2.1 on 2019-10-04 13:55

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('iotrec_api', '0012_category_value'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='value',
        ),
        migrations.RemoveField(
            model_name='user',
            name='preferences',
        ),
        migrations.CreateModel(
            name='Preference',
            fields=[
                ('id', models.UUIDField(default=None, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('value', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(-1), django.core.validators.MaxValueValidator(1)])),
                ('category', mptt.fields.TreeForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iotrec_api.Category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
