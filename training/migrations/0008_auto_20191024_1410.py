# Generated by Django 2.2.1 on 2019-10-24 14:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0007_baseline'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Baseline',
            new_name='ContextBaseline',
        ),
        migrations.AlterField(
            model_name='contextfactor',
            name='title',
            field=models.CharField(default='contextFactor', editable=False, max_length=128, unique=True),
        ),
        migrations.AlterField(
            model_name='contextfactorvalue',
            name='title',
            field=models.CharField(default='factorValue', editable=False, max_length=128),
        ),
        migrations.CreateModel(
            name='ThingBaseline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('value', models.FloatField(default=0, editable=False)),
                ('reference_thing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='training.ReferenceThing')),
            ],
        ),
    ]
