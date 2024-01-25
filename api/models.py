# Create your models here.
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class CustomUser(User):
    def save(self, *args, **kwargs):
        if (self.is_superuser or self.is_staff) and CustomUser.objects.filter(is_superuser=True).exists():
            raise ValidationError("Only one superuser is allowed")
        super().save(*args, **kwargs)


class UserMini(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=150)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_aproved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
