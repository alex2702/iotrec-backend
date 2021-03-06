# Generated by Django 2.2.1 on 2019-10-24 14:28

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0009_auto_20191024_1424'),
        ('iotrec_api', '0005_auto_20191016_1902'),
    ]

    operations = [
        migrations.AddField(
            model_name='iotrecsettings',
            name='category_weight',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='iotrecsettings',
            name='context_weight',
            field=models.FloatField(default=0, editable=False, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='iotrecsettings',
            name='locality_weight',
            field=models.FloatField(default=0, editable=False, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='iotrecsettings',
            name='nr_of_reference_things_per_thing',
            field=models.IntegerField(default=3),
        ),
        migrations.AddField(
            model_name='iotrecsettings',
            name='prediction_weight',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='thing',
            name='indoorsLocation',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='recommendation',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='iotrec_api.Recommendation'),
        ),
        migrations.AlterField(
            model_name='iotrecsettings',
            name='recommendation_threshold',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='rating',
            name='recommendation',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='iotrec_api.Recommendation'),
        ),
        migrations.CreateModel(
            name='Stay',
            fields=[
                ('id', models.CharField(editable=False, max_length=255, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('updated_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('start', models.DateTimeField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('last_checkin', models.DateTimeField(blank=True, null=True)),
                ('thing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iotrec_api.Thing')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SimilarityReference',
            fields=[
                ('id', models.CharField(editable=False, max_length=255, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('updated_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('similarity', models.FloatField(default=0, editable=False)),
                ('reference_thing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='training.ReferenceThing')),
                ('thing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iotrec_api.Thing')),
            ],
        ),
        migrations.CreateModel(
            name='Context',
            fields=[
                ('id', models.CharField(editable=False, max_length=255, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('updated_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('temperature_raw', models.IntegerField(default=0)),
                ('length_of_trip_raw', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('crowdedness', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='crowdedness', to='training.ContextFactorValue')),
                ('length_of_trip', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='length_of_trip', to='training.ContextFactorValue')),
                ('temperature', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='temperature', to='training.ContextFactorValue')),
                ('time_of_day', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='time_of_day', to='training.ContextFactorValue')),
                ('weather', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='weather', to='training.ContextFactorValue')),
            ],
        ),
        migrations.AddField(
            model_name='recommendation',
            name='context',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, to='iotrec_api.Context'),
            preserve_default=False,
        ),
    ]
