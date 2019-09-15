import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from enumchoicefield import EnumChoiceField
from mptt.fields import TreeManyToManyField

from iotrec_api.models import Category
from iotrec_api.utils.thing import ThingType


class ReferenceThing(models.Model):
    title = models.CharField(max_length=128, default='New Thing')
    description = models.TextField(blank=True)
    type = EnumChoiceField(ThingType, default=ThingType.BCN_I)
    image = models.ImageField(blank=True)
    categories = TreeManyToManyField(Category, blank=True)

    def __str__(self):
        return self.title


class TrainingUser(models.Model):
    identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return str(self.identifier)


class ContextFactor(models.Model):
    title = models.CharField(max_length=128, default='contextFactor')
    display_title = models.CharField(max_length=128, default='Context Factor')

    def __str__(self):
        return self.display_title


class ContextFactorValue(models.Model):
    title = models.CharField(max_length=128, default='factorValue')
    display_title = models.CharField(max_length=128, default='Factor Value')
    description = models.CharField(max_length=255, default='Factor Value Description')
    context_factor = models.ForeignKey(ContextFactor, related_name='values', on_delete=models.CASCADE)

    def __str__(self):
        return self.display_title


class Sample(models.Model):
    thing = models.ForeignKey(ReferenceThing, on_delete=models.CASCADE)
    context_factor = models.ForeignKey(ContextFactor, on_delete=models.CASCADE)
    context_factor_value = models.ForeignKey(ContextFactorValue, on_delete=models.CASCADE)
    value = models.IntegerField(validators=[MinValueValidator(-1), MaxValueValidator(1)], default=0)
    user = models.ForeignKey(TrainingUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.thing.title + "/" + self.context_factor.title + "/" + self.context_factor_value.title
