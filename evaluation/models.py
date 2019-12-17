import random
import uuid

from django.db import models
from django.utils import timezone
from enumchoicefield import EnumChoiceField
from rest_framework.compat import MinValueValidator, MaxValueValidator

from evaluation.utils.analyticsevent import AnalyticsEventType
from iotrec_api.utils.context import WeatherType, TemperatureType, LengthOfTripType, TimeOfDayType, CrowdednessType
from django.apps import apps


class Experiment(models.Model):
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey("iotrec_api.User", related_name="experiments", on_delete=models.CASCADE)
    scenario = models.ForeignKey("Scenario", on_delete=models.CASCADE, null=True, blank=True)
    context_active = models.BooleanField(editable=False, default=False)
    preferences_active = models.BooleanField(editable=False, default=False)
    order = models.IntegerField(editable=False, default=0)
    #context = models.OneToOneField("iotrec_api.Context", on_delete=models.CASCADE, null=True, blank=True)python

    def save(self, *args, **kwargs):
        
        if not self.pk:
            self.created_at = timezone.now()

            '''
            Context = apps.get_model("iotrec_api", "Context")

            # get a random weather choice
            random_weather = random.choice(list(WeatherType))

            # get a random temperature choice (depending on the weather)
            temp_choice = ""
            if random_weather == WeatherType.SUNNY:
                temp_choice = random.choice(list(TemperatureType))  # all temperatures are possible
            elif random_weather == WeatherType.CLOUDY:
                temp_choice = random.choice(list(TemperatureType))
            elif random_weather == WeatherType.SNOWY:
                temp_choice = random.choice([TemperatureType.COLD, TemperatureType.COOL])
            elif random_weather == WeatherType.RAINY:
                temp_choice = random.choice([TemperatureType.COOL, TemperatureType.MILD, TemperatureType.WARM])
            elif random_weather == WeatherType.WINDY:
                temp_choice = random.choice(list(TemperatureType))

            print("temp_choice: " + str(temp_choice))

            # get a random temperature for this choice
            if temp_choice is TemperatureType.COLD:
                temp_raw = random.randint(-20, 0)
            elif temp_choice is TemperatureType.COOL:
                temp_raw = random.randint(0, 10)
            elif temp_choice is TemperatureType.MILD:
                temp_raw = random.randint(10, 20)
            elif temp_choice is TemperatureType.WARM:
                temp_raw = random.randint(20, 30)
            elif temp_choice is TemperatureType.HOT:
                temp_raw = random.randint(30, 40)

            # get a random length_of_trip choice
            lot_choice = random.choice(list(LengthOfTripType))

            # get a random nr of minutes for this choice
            if lot_choice is LengthOfTripType.ONE_HR:
                lot_raw = random.randint(0, 61)
            elif lot_choice is LengthOfTripType.FEW_HRS:
                lot_raw = random.randint(61, 181)
            elif lot_choice is LengthOfTripType.MANY_HRS:
                lot_raw = random.randint(181, 601)

            self.context = Context.objects.create(
                weather_raw=random_weather,
                temperature_raw=temp_raw,
                length_of_trip_raw=lot_raw,
                time_of_day_raw=random.choice(list(TimeOfDayType)),
            )
            '''

        self.updated_at = timezone.now()
        super(Experiment, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username + " - " + self.scenario.title + " (C: " + str(self.context_active) + " - P: " + str(self.preferences_active) + ")"


class Question(models.Model):
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    short_name = models.CharField(max_length=255)
    text = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(Question, self).save(*args, **kwargs)

    def __str__(self):
        return self.short_name


class Reply(models.Model):
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    user = models.ForeignKey("iotrec_api.User", on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    experiment = models.ForeignKey("Experiment", on_delete=models.CASCADE)
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=3)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(Reply, self).save(*args, **kwargs)

    def __str__(self):
        return self.question.short_name + " (" + str(self.value) + ")"


class Questionnaire(models.Model):
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    user = models.ForeignKey("iotrec_api.User", on_delete=models.CASCADE)
    age = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    qualification = models.CharField(max_length=255, null=True, blank=True)
    smartphone_usage = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(Questionnaire, self).save(*args, **kwargs)


class AnalyticsEvent(models.Model):
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    type = EnumChoiceField(AnalyticsEventType, null=True, blank=True)
    user = models.ForeignKey("iotrec_api.User", on_delete=models.CASCADE, null=True, blank=True)
    thing = models.ForeignKey("iotrec_api.Thing", on_delete=models.CASCADE, null=True, blank=True)
    recommendation = models.ForeignKey("iotrec_api.Recommendation", on_delete=models.CASCADE, null=True, blank=True)
    value = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(AnalyticsEvent, self).save(*args, **kwargs)


class Scenario(models.Model):
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    text_id = models.CharField(max_length=128, primary_key=True)
    title = models.CharField(max_length=128, null=False, blank=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(Scenario, self).save(*args, **kwargs)

    def __str__(self):
        return self.title