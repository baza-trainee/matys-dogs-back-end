from django.db import models
from backblaze.models import FileModel
# Create your models here.


class NewsModel(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=False)
    post_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    sub_text = models.CharField(max_length=100, null=True)
    url = models.URLField(max_length=300)
    photo = models.ForeignKey(
        FileModel, on_delete=models.CASCADE, null=True, blank=True)

    def photo_url(self):
        return self.photo.url

    class Meta:
        ordering = ['-post_at', '-update_at']


class Partners(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    logo = models.ForeignKey(
        FileModel, on_delete=models.CASCADE, null=True, blank=True)

    def logo_url(self):
        return self.logo.url

    class Meta:
        ordering = ['name']
