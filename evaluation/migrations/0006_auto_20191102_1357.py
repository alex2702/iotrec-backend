# Generated by Django 2.2.1 on 2019-11-02 13:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0005_auto_20191102_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='scenario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='evaluation.Scenario'),
        ),
    ]
