# Create your models here.
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class CustomUser(User):
    def save(self, *args, **kwargs):
        if (self.is_superuser or self.is_staff) and CustomUser.objects.filter(is_superuser=True).exists():
            raise ValidationError("Only one superuser is allowed")
        super().save(*args, **kwargs)


class BasicAdmin():
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        abstract = True
