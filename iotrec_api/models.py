import math
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
    nr_of_items_flat = models.IntegerField(default=0)
    nr_of_items_recursive = models.IntegerField(default=0)

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

'''
class ThingManager(models.Manager):
    def get_similarity(self, other):
        # get all categories that "self" is classified in
        categories_self = set()
        for category in range(len(self.categories)):
            if category not in categories_self:
                categories_self.add(category)
                while category.parent is not None:
                    category = category.parent
                    if category not in categories_self:
                        categories_self.add(category)

        # get all categories that "other" (a thing or a user) is classified in
        categories_other = set()
        for category in range(len(other.categories)):
            if category not in categories_other:
                categories_other.add(category)
                while category.parent is not None:
                    category = category.parent
                    if category not in categories_other:
                        categories_other.add(category)

        # merge the category lists
        categories = categories_self.union(categories_other)

        divident = 0
        divisor_inner_self = 0
        divisor_inner_other = 0

        # for each category i
        for cat in categories:
            # 1 if self has category i, 0 otherwise
            tf_self_i = 1 if (cat in categories_self) else 0

            # 1 if other has category i, 0 otherwise
            tf_other_i = 1 if (cat in categories_other) else 0

            # number of items classified in subtree for which the parent of i is the root
            n_p_i = cat.parent.thing_set

            # number of items classified in subtree for which i is the root
            n_i =

            factor_self = tf_self_i * math.log(n_p_i/n_i)
            factor_other = tf_other_i * math.log(n_p_i/n_i)

            divident += factor_self * factor_other
            divisor_inner_self += factor_self * factor_self
            divisor_inner_other += factor_other * factor_other

        result = divident / (math.sqrt(divisor_inner_self) * math.sqrt(divisor_inner_other))

        return result
'''


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
    #objects = ThingManager()

    def save(self, *args, **kwargs):
        self.id = '{0}-{1}-{2}'.format(self.uuid, self.major_id, self.minor_id)

        '''
        # go through all categories of this thing
            # cycle through 
        for cat in self.categories:
            Thing.objects.all
        '''

        super(Thing, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    #def clean_id(self):
    #    return '{0}-{1}-{2}'.format(self.uuid, self.major_id, self.minor_id)
