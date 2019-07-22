import uuid as uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from enumchoicefield import ChoiceEnum, EnumChoiceField
from location_field.models.plain import PlainLocationField

from iotrec_api.utils.thing import ThingType


class IotRecUser(AbstractUser):
    """DB model for Users"""
    is_administrator = models.BooleanField(default=False)


"""
class Venue(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    image = models.ImageField(blank=True)
"""


class Thing(models.Model):

    id = models.CharField(max_length=128, default='00000000-0000-0000-0000-000000000000-0-0', primary_key=True)
    title = models.CharField(max_length=128, default='New Thing')
    description = models.TextField(blank=True)
    # type = models.CharField(max_length=255, choices=ThingType.choices())
    type = EnumChoiceField(ThingType, default=ThingType.BCN_I)
    uuid = models.UUIDField(default='00000000-0000-0000-0000-000000000000')
    major_id = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(65535)], default=0)
    minor_id = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(65535)], default=0)
    image = models.ImageField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    # venue = models.ForeignKey("Venue", on_delete=models.PROTECT, null=True)
    address = models.CharField(max_length=255, blank=True)
    location = PlainLocationField(based_fields=['address'], blank=True)

    def save(self, **kwargs):
        self.id = '{0}-{1}-{2}'.format(self.uuid, self.major_id, self.minor_id)
        super().save(*kwargs)