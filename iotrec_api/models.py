import math
import uuid as uuid

from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from enumchoicefield import ChoiceEnum, EnumChoiceField
from location_field.models.plain import PlainLocationField
from mptt.fields import TreeForeignKey, TreeManyToManyField
from mptt.models import MPTTModel
from django.core.exceptions import ValidationError
from rest_framework import exceptions

from iotrec_api.utils.analyticsevent import AnalyticsEventType
from iotrec_api.utils.context import WeatherType, TemperatureType, LengthOfTripType, CrowdednessType, TimeOfDayType
from iotrec_api.utils.recommendation import get_recommendation_score
from iotrec_api.utils.similarity_reference import calculate_similarity_references_per_thing
from iotrec_api.utils.thing import ThingType, get_utility


# source: https://steelkiwi.com/blog/practical-application-singleton-design-pattern/
from training.models import ContextFactor, ContextFactorValue


class IotRecSettings(models.Model):
    recommendation_threshold = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], default=0)
    nr_of_reference_things_per_thing = models.IntegerField(default=3)
    category_weight = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], default=0)
    locality_weight = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], default=0, editable=False)
    prediction_weight = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], default=0)
    context_weight = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], default=0, editable=False)

    def save(self, *args, **kwargs):
        self.pk = 1
        self.locality_weight = 1 - self.category_weight
        self.context_weight = 1 - self.prediction_weight
        super(IotRecSettings, self).save(*args, **kwargs)
        self.set_cache()

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)

    def set_cache(self):
        cache.set(self.__class__.__name__, self)


class Category(MPTTModel):
    # parent = models.ForeignKey('self', null=True, blank=True, related_name='subcategories', on_delete=models.CASCADE)
    text_id = models.CharField(max_length=255, primary_key=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True,
                            on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_alias = models.BooleanField(default=False)
    alias_owner = TreeForeignKey('self', null=True, blank=True, related_name='target', db_index=True,
                                 on_delete=models.CASCADE)
    #nr_of_items_flat = models.IntegerField(default=0) # TODO maybe use this to make calculations more efficient?
    #nr_of_items_recursive = models.IntegerField(default=0) # TODO maybe use this to make calculations more efficient?

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'Categories'

    # class Meta:
    #    ordering = ('tree_id', 'level')


class User(AbstractUser):
    """DB model for Users"""
    # is_administrator = models.BooleanField(default=False) # TODO remove
    # preferences = TreeManyToManyField('Category', blank=True)


"""
class Venue(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    image = models.ImageField(blank=True)
"""

class Thing(models.Model):
    id = models.CharField(max_length=128, default=None, primary_key=True)
    title = models.CharField(max_length=128, default='New Thing')
    description = models.TextField(blank=True)
    type = EnumChoiceField(ThingType, default=ThingType.BCN_I)
    uuid = models.UUIDField(default=uuid.uuid4)
    major_id = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(65535)], default=0)
    minor_id = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(65535)], default=0)
    image = models.ImageField(blank=True)
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    location = PlainLocationField(based_fields=['address'], blank=True)
    categories = TreeManyToManyField('Category', blank=True)
    indoorsLocation = models.BooleanField(default=None, blank=True, null=True)

    #def clean(self):
    #    for category in self.categories.all():
    #        print(category)
    #        if category.get_level() < 2:
    #            raise ValidationError({
    #                'categories': ValidationError(_('Selected categories must be in level 2.'), code='invalid'),
    #            })
    #    super(Thing, self).clean()

    #def clean_categories(self):
    #    print("clean_categories in Thing model")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        self.id = '{0}-{1}-{2}'.format(self.uuid, self.major_id, self.minor_id)

        try:
            self.full_clean()
            super(Thing, self).save(*args, **kwargs)
        except ValidationError as e:
            raise exceptions.ValidationError({'id': ["Thing with this Id already exists.", ]})

    def __str__(self):
        return self.title

    # def calculate_similarity(self, other):

    # def clean_id(self):
    #    return '{0}-{1}-{2}'.format(self.uuid, self.major_id, self.minor_id)


class Recommendation(models.Model):
    id = models.UUIDField(default=None, primary_key=True, editable=False)
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    thing = models.ForeignKey("Thing", on_delete=models.CASCADE)
    context = models.OneToOneField("Context", on_delete=models.CASCADE)
    invoke_rec = models.BooleanField(editable=False, default=False)
    score = models.FloatField(editable=False, default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = uuid.uuid4()
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        self.score = get_recommendation_score(self.thing, self.user, self.context)
        self.invoke_rec = self.get_invoke_rec(self.score)

        try:
            self.full_clean()
            super(Recommendation, self).save(*args, **kwargs)
        except ValidationError as e:
            print(e)
            #raise exceptions.ValidationError({'id': ["Thing with this Id already exists.", ]})


    def __str__(self):
        return str(self.id)

    def get_invoke_rec(self, score, *args, **kwargs):
        settings = IotRecSettings.load()
        return score > settings.recommendation_threshold


class Feedback(models.Model):
    VALUE_CHOICES = [
        (-1, '-1'),
        (1, '1'),
    ]

    id = models.UUIDField(default=None, primary_key=True, editable=False)
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    recommendation = models.OneToOneField("Recommendation", on_delete=models.CASCADE)
    value = models.IntegerField(choices=VALUE_CHOICES, default=0)

    #def validate_unique(self, exclude=None):
    #    # reject if the given recommendation has a feedback already
    #    if Feedback.objects.filter(recommendation=self.recommendation).exists():
    #        raise ValidationError({'recommendation': ["The recommendation already has received feedback.", ]})

    def save(self, *args, **kwargs):
    #    self.validate_unique()
        if not self.pk:
            self.pk = uuid.uuid4()
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(Feedback, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class Rating(models.Model):
    id = models.UUIDField(default=None, primary_key=True, editable=False)
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    recommendation = models.OneToOneField("Recommendation", on_delete=models.CASCADE)
    value = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    improvements = models.CharField(max_length=1024, null=True, blank=True)

    #def validate_unique(self, exclude=None):
    #    # reject if the given recommendation has a feedback already
    #    if Rating.objects.filter(recommendation=self.recommendation).exists():
    #        raise ValidationError({'recommendation': ["The recommendation already has received a rating.", ]})

    def save(self, *args, **kwargs):
    #    self.validate_unique()
        if not self.pk:
            self.pk = uuid.uuid4()
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(Rating, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class Preference(models.Model):
    VALUE_CHOICES = [
        (-1, '-1'),
        (1, '1'),
    ]

    #id = models.UUIDField(default=None, primary_key=True, editable=False)
    id = models.CharField(max_length=255, primary_key=True, editable=False)
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    category = TreeForeignKey("Category", on_delete=models.CASCADE)
    value = models.IntegerField(choices=VALUE_CHOICES, default=0)
    user = models.ForeignKey("User", related_name="preferences", on_delete=models.CASCADE)

    def validate_unique(self, exclude=None):
        # get all preferences of the given user
        user_prefs = Preference.objects.filter(user=self.user)
        # reject new preference if user has it already
        if user_prefs.filter(category=self.category).exists():
            raise ValidationError({'category': ["The user already has that preference.", ]})

    def save(self, *args, **kwargs):
        self.validate_unique()
        if not self.pk:
            self.pk = self.category.text_id
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(Preference, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.category) + " (" + str(self.value) + ")"


class SimilarityReference(models.Model):
    id = models.CharField(max_length=255, primary_key=True, editable=False)
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    reference_thing = models.ForeignKey('training.ReferenceThing', on_delete=models.CASCADE)
    thing = models.ForeignKey("Thing", on_delete=models.CASCADE)
    similarity = models.FloatField(editable=False, default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = uuid.uuid4()
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(SimilarityReference, self).save(*args, **kwargs)


class Stay(models.Model):
    id = models.CharField(max_length=255, primary_key=True, editable=False)
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    thing = models.ForeignKey("Thing", on_delete=models.CASCADE)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    start = models.DateTimeField(editable=True, null=True, blank=True) # TODO make non-editable
    end = models.DateTimeField(editable=True, null=True, blank=True) # TODO make non-editable
    last_checkin = models.DateTimeField(editable=True, null=True, blank=True) # TODO make non-editable

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = uuid.uuid4()
            self.created_at = timezone.now()
            self.start = timezone.now()
            self.last_checkin = timezone.now()
        self.updated_at = timezone.now()
        super(Stay, self).save(*args, **kwargs)

    def __str__(self):
        return '{} ({} - {})'.format(self.pk, self.start, self.last_checkin)


class Context(models.Model):
    id = models.CharField(max_length=255, primary_key=True, editable=False)
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    weather_raw = EnumChoiceField(WeatherType, null=True)
    temperature_raw = models.IntegerField(default=0)
    length_of_trip_raw = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    crowdedness_raw = EnumChoiceField(CrowdednessType, null=True)
    time_of_day_raw = EnumChoiceField(TimeOfDayType, null=True)
    weather = models.ForeignKey('training.ContextFactorValue', related_name='weather', on_delete=models.SET_NULL, null=True)
    temperature = models.ForeignKey('training.ContextFactorValue', related_name='temperature', on_delete=models.SET_NULL, null=True)
    length_of_trip = models.ForeignKey('training.ContextFactorValue', related_name='length_of_trip', on_delete=models.SET_NULL, null=True)
    crowdedness = models.ForeignKey('training.ContextFactorValue', related_name='crowdedness', on_delete=models.SET_NULL, blank=True, null=True)
    time_of_day = models.ForeignKey('training.ContextFactorValue', related_name='time_of_day', on_delete=models.SET_NULL, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = uuid.uuid4()
            self.created_at = timezone.now()
        self.updated_at = timezone.now()

        # set temperature
        cf_temperature = ContextFactor.objects.get(title='temperature')
        if self.temperature_raw < 0:
            self.temperature = ContextFactorValue.objects.get(context_factor=cf_temperature, title='cold')
        elif 0 >= self.temperature_raw < 10:
            self.temperature = ContextFactorValue.objects.get(context_factor=cf_temperature, title='cool')
        elif 10 >= self.temperature_raw < 20:
            self.temperature = ContextFactorValue.objects.get(context_factor=cf_temperature, title='mild')
        elif 20 >= self.temperature_raw < 30:
            self.temperature = ContextFactorValue.objects.get(context_factor=cf_temperature, title='warm')
        else:
            self.temperature = ContextFactorValue.objects.get(context_factor=cf_temperature, title='hot')

        # set length_of_trip
        cf_length_of_trip = ContextFactor.objects.get(title='durationOfTrip')
        if self.length_of_trip_raw <= 60:
            self.length_of_trip = ContextFactorValue.objects.get(context_factor=cf_length_of_trip, title='upToAnHour')
        elif 60 < self.length_of_trip_raw <= 180:
            self.length_of_trip = ContextFactorValue.objects.get(context_factor=cf_length_of_trip, title='aFewHours')
        else:
            self.length_of_trip = ContextFactorValue.objects.get(context_factor=cf_length_of_trip, title='manyHours')

        # set weather
        cf_weather = ContextFactor.objects.get(title='weather')
        if self.weather_raw == WeatherType.SUNNY:
            self.weather = ContextFactorValue.objects.get(context_factor=cf_weather, title='sunny')
        elif self.weather_raw == WeatherType.CLOUDY:
            self.weather = ContextFactorValue.objects.get(context_factor=cf_weather, title='cloudy')
        elif self.weather_raw == WeatherType.SNOWY:
            self.weather = ContextFactorValue.objects.get(context_factor=cf_weather, title='snowy')
        elif self.weather_raw == WeatherType.RAINY:
            self.weather = ContextFactorValue.objects.get(context_factor=cf_weather, title='rainy')
        elif self.weather_raw == WeatherType.WINDY:
            self.weather = ContextFactorValue.objects.get(context_factor=cf_weather, title='windy')

        # set crowdedness
        cf_crowdedness = ContextFactor.objects.get(title='crowdedness')
        if self.crowdedness_raw == CrowdednessType.VERY_CROWDED:
            self.crowdedness = ContextFactorValue.objects.get(context_factor=cf_crowdedness, title='veryCrowded')
        elif self.crowdedness_raw == CrowdednessType.MEDIUM_CROWDED:
            self.crowdedness = ContextFactorValue.objects.get(context_factor=cf_crowdedness, title='mediumCrowded')
        elif self.crowdedness_raw == CrowdednessType.EMPTY:
            self.crowdedness = ContextFactorValue.objects.get(context_factor=cf_crowdedness, title='empty')

        # set time of day
        cf_time_of_day = ContextFactor.objects.get(title='timeOfDay')
        if self.time_of_day_raw == TimeOfDayType.EARLY_MORNING:
            self.time_of_day = ContextFactorValue.objects.get(context_factor=cf_time_of_day, title='earlyMorning')
        elif self.time_of_day_raw == TimeOfDayType.LATE_MORNING:
            self.time_of_day = ContextFactorValue.objects.get(context_factor=cf_time_of_day, title='lateMorning')
        elif self.time_of_day_raw == TimeOfDayType.NOON:
            self.time_of_day = ContextFactorValue.objects.get(context_factor=cf_time_of_day, title='noon')
        elif self.time_of_day_raw == TimeOfDayType.AFTERNOON:
            self.time_of_day = ContextFactorValue.objects.get(context_factor=cf_time_of_day, title='afternoon')
        elif self.time_of_day_raw == TimeOfDayType.EVENING:
            self.time_of_day = ContextFactorValue.objects.get(context_factor=cf_time_of_day, title='evening')
        elif self.time_of_day_raw == TimeOfDayType.NIGHT:
            self.time_of_day = ContextFactorValue.objects.get(context_factor=cf_time_of_day, title='night')

        super(Context, self).save(*args, **kwargs)


class AnalyticsEvent(models.Model):
    id = models.CharField(max_length=255, primary_key=True, editable=False)
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    type = EnumChoiceField(AnalyticsEventType, null=True, blank=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True, blank=True)
    thing = models.ForeignKey("Thing", on_delete=models.CASCADE, null=True, blank=True)
    recommendation = models.ForeignKey("Recommendation", on_delete=models.CASCADE, null=True, blank=True)
    value = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = uuid.uuid4()
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(AnalyticsEvent, self).save(*args, **kwargs)
