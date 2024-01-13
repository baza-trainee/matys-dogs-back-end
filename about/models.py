from django.db import models
from backblaze.models import FileModel
from django.core.exceptions import ValidationError
# Create your models here.


class AboutModel(models.Model):
    quantity_of_animals = models.IntegerField()
    quantity_of_employees = models.IntegerField()
    quantity_of_succeeds_adoptions = models.IntegerField()
    images = models.ManyToManyField(
        FileModel, related_name='about_images')

    def imges_url(self):
        return [image.url for image in self.images.all()]

    def save(self, *args, **kwargs):
        if AboutModel.objects.exists() and not self.pk:
            raise ValidationError(
                'There is can be only one AboutModel instance')
        super(AboutModel, self).save(*args, **kwargs)
