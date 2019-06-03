import uuid as uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class Thing(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=True)
    major_id = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(65535)])
    minor_id = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(65535)])
    title = models.CharField(max_length=128)
    description = models.TextField()
    image = models.ImageField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)