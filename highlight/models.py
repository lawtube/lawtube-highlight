from django.db import models
from django.urls.converters import uuid

# Create your models here.
class Highlight(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid4)
    link = models.CharField(max_length=255)
    progress = models.IntegerField()
    highlight_link = models.CharField(max_length=255, null=True)
    timestamp = models.JSONField()
