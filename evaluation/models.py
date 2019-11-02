from django.db import models
from django.utils import timezone
from enumchoicefield import EnumChoiceField
from rest_framework.compat import MinValueValidator, MaxValueValidator

from evaluation.utils.analyticsevent import AnalyticsEventType


class Experiment(models.Model):
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey("iotrec_api.User", on_delete=models.CASCADE)
    scenario = models.ForeignKey("Scenario", on_delete=models.CASCADE, null=True, blank=True)
    context_active = models.BooleanField(editable=False, default=False)
    preferences_active = models.BooleanField(editable=False, default=False)
    order = models.IntegerField(editable=False, default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(Experiment, self).save(*args, **kwargs)


class Question(models.Model):
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    title = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(Question, self).save(*args, **kwargs)


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


class Questionnaire(models.Model):
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    user = models.ForeignKey("iotrec_api.User", on_delete=models.CASCADE)
    # TODO add fields for replies

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
