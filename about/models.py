from django.db import models
from backblaze.models import FileModel
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.


class AboutModel(models.Model):
    quantity_of_animals = models.IntegerField(
        validators=[MaxValueValidator(1000), MinValueValidator(0)]
    )
    quantity_of_employees = models.IntegerField(
        validators=[MaxValueValidator(1000), MinValueValidator(0)]
    )
    quantity_of_succeeds_adoptions = models.IntegerField(
        validators=[MaxValueValidator(1000), MinValueValidator(0)]
    )
    images = models.ManyToManyField(FileModel, related_name="about_images")

    def imges_url(self):
        return [image.url for image in self.images.all()]

    def save(self, *args, **kwargs):
        if AboutModel.objects.exists() and not self.pk:
            raise ValidationError("There is can be only one AboutModel instance")
        super(AboutModel, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Про нас"
        verbose_name_plural = "Про нас"
        
