from django.db import models
from dog_card.models import DogCardModel

# Create your models here.


class CallbackForm(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25, null=False)
    phone_number = models.CharField(max_length=20, null=False)
    comment = models.TextField(blank=True, null=True, max_length=100)
    id_dog = models.ForeignKey(DogCardModel, on_delete=models.DO_NOTHING, null=False)

    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    processing = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.name
