# Create your models here.
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class CustomUser(User):
    def save(self, *args, **kwargs):
        if (self.is_superuser or self.is_staff) and CustomUser.objects.filter(is_superuser=True).exists():
            raise ValidationError("Only one superuser is allowed")
        super().save(*args, **kwargs)
