from django.db import models
from backblaze.models import FileModel
# Create your models here.


class NewsManager(models.Manager):
    def get_lastest(self, limit=4):
        return self.get_queryset().order_by('-post_at', '-update_at')[:limit]


class NewsModel(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=60, blank=False)
    post_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    sub_text = models.CharField(max_length=150, null=True)
    url = models.URLField(max_length=300)
    photo = models.ForeignKey(
        FileModel, on_delete=models.CASCADE)

    objects = NewsManager()

    def photo_url(self):
        if self.photo:
            return self.photo.url
        return None

    class Meta:
        ordering = ['-post_at', '-update_at']
        


class Partners(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    website = models.URLField(max_length=300, null=True, blank=True)
    logo = models.ForeignKey(
        FileModel, on_delete=models.CASCADE, null=True, blank=True)

    def logo_url(self):
        return self.logo.url

    class Meta:
        ordering = ['name']
