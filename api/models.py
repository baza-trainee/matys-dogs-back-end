from django.db import models

# Create your models here.
class UserModel(models.Model):
    email = models.EmailField(unique=True)
    passwordHash = models.CharField(max_length=100)
