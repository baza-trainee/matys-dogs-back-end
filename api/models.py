from rest_framework import permissions
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class CustomUser(User):
    def save(self, *args, **kwargs):
        if (self.is_superuser or self.is_staff) and CustomUser.objects.filter(
            is_superuser=True
        ).exists():
            raise ValidationError("Only one superuser is allowed")
        super().save(*args, **kwargs)


class UserMini(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="usermini", null=True
    )
    is_approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User Mini"
        verbose_name_plural = "Users Mini"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def save(self, *args, **kwargs):
        if self.user.is_superuser:
            if (
                UserMini.objects.exclude(pk=self.pk)
                .filter(user__is_superuser=True)
                .exists()
            ):
                raise ValidationError("There can be only one superuser.")
        super().save(*args, **kwargs)


class IsApprovedUser(permissions.BasePermission):
    message = "User is not approved."

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        else:
            return (
                hasattr(request.user, "usermini") and request.user.usermini.is_approved
            )
