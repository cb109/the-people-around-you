from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    avatar = models.ImageField(upload_to="avatars", default=None, null=True, blank=True)

    # Additional fields to support representation as a Fabric.js object.
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    angle = models.IntegerField(default=0)
    scale = models.FloatField(default=1.0)
