# Generated by Django 2.2.1 on 2019-10-24 14:49

from django.db import migrations
import enumchoicefield.fields
import iotrec_api.utils.context


class Migration(migrations.Migration):

    dependencies = [
        ('iotrec_api', '0007_auto_20191024_1447'),
    ]

    operations = [
        migrations.AddField(
            model_name='context',
            name='crowdedness_raw',
            field=enumchoicefield.fields.EnumChoiceField(enum_class=iotrec_api.utils.context.CrowdednessType, max_length=14, null=True),
        ),
        migrations.AddField(
            model_name='context',
            name='time_of_day_raw',
            field=enumchoicefield.fields.EnumChoiceField(enum_class=iotrec_api.utils.context.TimeOfDayType, max_length=13, null=True),
        ),
    ]