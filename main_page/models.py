from django.db import models
from backblaze.models import FileModel
from backblaze.utils.b2_utils import delete_file_from_backblaze

# Create your models here.


class NewsManager(models.Manager):
    def get_lastest(self, limit=4):
        return self.get_queryset()[:limit]


class NewsModel(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=60, blank=False)
    post_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    sub_text = models.CharField(max_length=175, null=False, blank=False)
    url = models.URLField(max_length=300)
    photo = models.ForeignKey(FileModel, on_delete=models.CASCADE, null=True)

    objects = NewsManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        MAX_ITEMS = 4
        if NewsModel.objects.count() > MAX_ITEMS:
            oldest_news = NewsModel.objects.all().order_by("post_at").first()
            if oldest_news.photo is not None:
                delete_file_from_backblaze(oldest_news.photo_id)
                oldest_news.photo.delete()
            oldest_news.delete()

    def photo_url(self):
        if self.photo:
            return self.photo.url
        return None

    class Meta:
        ordering = ["-post_at"]
        verbose_name = "Новина"
        verbose_name_plural = "Новини"


class Partners(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    website = models.URLField(max_length=300, blank=False, null=False)
    logo = models.ForeignKey(FileModel, on_delete=models.CASCADE)

    def logo_url(self):
        return self.logo.url

    class Meta:
        ordering = ["name"]
        verbose_name = "Партнер"
        verbose_name_plural = "Партнери"
