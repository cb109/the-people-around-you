from django.db import models

from django.contrib.auth.models import AbstractUser


class TimestampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(TimestampedMixin, AbstractUser):
    pass


class Person(TimestampedMixin, models.Model):
    first_name = models.CharField(max_length=128, default="")
    last_name = models.CharField(max_length=128, default="")

    created_by = models.ForeignKey(
        User, default=None, null=True, on_delete=models.CASCADE
    )
    """Determines who gets to see/edit this."""

    avatar = models.ImageField(upload_to="avatars", default=None, null=True, blank=True)

    # Additional fields to support representation as a Konva/Fabric.js object.
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    angle = models.FloatField(default=0)
    scale = models.FloatField(default=1.0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def avatar_url(self):
        person_image = self.person_images.last()
        if person_image:
            return person_image.image.file.url
        return None

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name", "created_by"],
                name="unique_person_name_per_creator",
            )
        ]


class Image(TimestampedMixin, models.Model):
    file = models.ImageField(upload_to="images")

    def __str__(self):
        return self.file.name


class PersonImage(TimestampedMixin, models.Model):
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="person_images"
    )
    image = models.ForeignKey(
        Image, on_delete=models.CASCADE, related_name="person_images"
    )

    def __str__(self):
        return f"{self.person} -> {self.image}"
