import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from enumchoicefield import EnumChoiceField
from mptt.fields import TreeManyToManyField

from iotrec_api.utils.thing import ThingType


class ReferenceThing(models.Model):
    title = models.CharField(max_length=128, default='newThing')
    display_title = models.CharField(max_length=128, default='New Thing')
    description = models.TextField(blank=True)
    type = EnumChoiceField(ThingType, default=ThingType.BCN_I)
    image = models.ImageField(blank=True)
    categories = TreeManyToManyField('iotrec_api.Category', blank=True)
    indoorsLocation = models.BooleanField(default=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class TrainingUser(models.Model):
    identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.identifier)


class ContextFactor(models.Model):
    title = models.CharField(max_length=128, default='contextFactor', editable=False, unique=True)
    display_title = models.CharField(max_length=128, default='Context Factor')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_title


class ContextFactorValue(models.Model):
    title = models.CharField(max_length=128, default='factorValue', editable=False)
    display_title = models.CharField(max_length=128, default='Factor Value')
    description = models.CharField(max_length=255, default='Factor Value Description')
    context_factor = models.ForeignKey(ContextFactor, related_name='values', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_title


class Sample(models.Model):
    thing = models.ForeignKey(ReferenceThing, on_delete=models.CASCADE)
    context_factor = models.ForeignKey(ContextFactor, on_delete=models.CASCADE)
    context_factor_value = models.ForeignKey(ContextFactorValue, on_delete=models.CASCADE)
    value = models.IntegerField(validators=[MinValueValidator(-1), MaxValueValidator(1)], default=0)
    user = models.ForeignKey(TrainingUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.thing.title + "/" + self.context_factor.title + "/" + self.context_factor_value.title


class ContextBaseline(models.Model):
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    reference_thing = models.ForeignKey("ReferenceThing", on_delete=models.CASCADE)
    context_factor = models.ForeignKey("ContextFactor", on_delete=models.CASCADE)
    context_factor_value = models.ForeignKey("ContextFactorValue", on_delete=models.CASCADE)
    value = models.FloatField(editable=False, default=0)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super(ContextBaseline, self).save(*args, **kwargs)


class ThingBaseline(models.Model):
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    reference_thing = models.ForeignKey("ReferenceThing", on_delete=models.CASCADE)
    value = models.FloatField(editable=False, default=0)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super(ThingBaseline, self).save(*args, **kwargs)