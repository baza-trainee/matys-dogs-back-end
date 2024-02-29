from django.db import models

# Create your models here.


class FileModel(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200, blank=False)
    url = models.URLField(max_length=200, blank=False)
    category = models.CharField(max_length=20, blank=False)

    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"
