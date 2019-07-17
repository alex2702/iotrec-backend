import uuid as uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from enumchoicefield import ChoiceEnum, EnumChoiceField
from iotrec_api.utils.thing import ThingType


class IotRecUser(AbstractUser):
    """DB model for Users"""
    is_administrator = models.BooleanField(default=False)


class Venue(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    image = models.ImageField(blank=True)


class Thing(models.Model):
    # type = models.CharField(max_length=255, choices=ThingType.choices())
    type = EnumChoiceField(ThingType, default=ThingType.IBEAC)
    uuid = models.UUIDField(default=uuid.uuid4)
    major_id = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(65535)], default=0)
    minor_id = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(65535)], default=0)
    # title = models.CharField(max_length=128)
    # description = models.TextField()
    # image = models.ImageField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    venue = models.ForeignKey("Venue", on_delete=models.PROTECT, null=True)
