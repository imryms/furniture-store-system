from django.db import models
from django.contrib.auth.models import AbstractUser


class Branch(models.Model):
    name    = models.CharField(max_length=100)
    address = models.TextField()
    phone   = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class User(AbstractUser):
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.get_full_name()}"
