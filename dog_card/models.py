from django.db import models
from backblaze.models import FileModel

# Create your models here.


class DogCardModel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25)
    ready_for_adoption = models.BooleanField(default=False)
    gender = models.CharField(
        max_length=10,
        choices=[
            ("хлопчик", "хлопчик"),
            ("дівчинка", "дівчинка"),
            ("boy", "boy"),
            ("girl", "girl"),
        ],
    )
    age = models.CharField(max_length=20)
    sterilization = models.BooleanField(default=False)
    vaccination_parasite_treatment = models.BooleanField(default=False)
    size = models.CharField(
        max_length=10,
        choices=[
            ("маленький", "маленький"),
            ("середній", "середній"),
            ("великий", "великий"),
            ("small", "small"),
            ("medium", "medium"),
            ("large", "large"),
        ],
    )
    description = models.TextField()
    photo = models.ForeignKey(
        FileModel,
        on_delete=models.CASCADE,
        limit_choices_to=models.Q(category="image"),
        blank=True,
        null=True,
    )

    def photo_url(self):
        return self.photo.url

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]
        verbose_name = "Картка собаки"
        verbose_name_plural = "Картки собак"
        
        
        
