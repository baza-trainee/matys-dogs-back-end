from django.db import models
from backblaze.models import FileModel
# Create your models here.


class NewsModel(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    post_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    sub_text = models.CharField(max_length=100)
    Text = models.TextField()
    photo = models.ForeignKey(FileModel, on_delete=models.CASCADE, limit_choices_to=models.Q(
        category='image'), null=True, blank=True)

    def photo_url(self):
        return self.photo.url
