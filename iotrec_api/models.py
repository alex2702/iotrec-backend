from django.db import models

class Thing(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    image = models.ImageField()
    created_at = models.DateTimeField(auto_now_add=True)