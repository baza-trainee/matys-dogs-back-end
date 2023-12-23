from django.db import models

# Create your models here.
class FileModel(models.Model):
    name = models.CharField(max_length=200, blank=False)
    url = models.URLField(max_length=200, blank=True)
    category = models.CharField(max_length=200, blank=False)