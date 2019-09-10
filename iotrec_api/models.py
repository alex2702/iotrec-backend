import uuid as uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from enumchoicefield import ChoiceEnum, EnumChoiceField
from location_field.models.plain import PlainLocationField
from mptt.fields import TreeForeignKey, TreeManyToManyField
from mptt.models import MPTTModel

from iotrec_api.utils.thing import ThingType


class Category(MPTTModel):
    #parent = models.ForeignKey('self', null=True, blank=True, related_name='subcategories', on_delete=models.CASCADE)
    text_id = models.CharField(max_length=255, primary_key=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_alias = models.BooleanField(default=False)
    alias_owner = TreeForeignKey('self', null=True, blank=True, related_name='target', db_index=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'Categories'

    #class Meta:
    #    ordering = ('tree_id', 'level')


class User(AbstractUser):
    """DB model for Users"""
    #is_administrator = models.BooleanField(default=False) # TODO remove
    preferences = TreeManyToManyField('Category', blank=True)


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
    # categories = models.ManyToManyField(Category)
    categories = TreeManyToManyField('Category', blank=True)

    def save(self, **kwargs):
        self.id = '{0}-{1}-{2}'.format(self.uuid, self.major_id, self.minor_id)
        super().save(*kwargs)

    def __str__(self):
        return self.title

