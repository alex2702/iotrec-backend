# Generated by Django 2.2.1 on 2019-07-21 06:30

from django.db import migrations, models
import enumchoicefield.fields
import iotrec_api.utils.thing


class Migration(migrations.Migration):

    dependencies = [
        ('iotrec_api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thing',
            name='venue',
        ),
        migrations.AddField(
            model_name='thing',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='thing',
            name='image',
            field=models.ImageField(blank=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='thing',
            name='title',
            field=models.CharField(default='New Thing', max_length=128),
        ),
        migrations.AlterField(
            model_name='thing',
            name='type',
            field=enumchoicefield.fields.EnumChoiceField(default=iotrec_api.utils.thing.ThingType(1), enum_class=iotrec_api.utils.thing.ThingType, max_length=8),
        ),
        migrations.DeleteModel(
            name='Venue',
        ),
    ]
