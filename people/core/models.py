import os

from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image as PIL_Image


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
            if person_image.image.preview.name:
                return person_image.image.preview.url
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
    """Original upload of cropped avatar."""

    preview = models.ImageField(upload_to="images", default=None, null=True, blank=True)
    """Normalized 300x300 version for use in graph."""

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.file.name and not self.preview.name:
            self._make_preview()

    def _make_preview(self):
        suffix = "_300x300"
        try:
            ext = os.path.splitext(self.file.name)[1]
            preview_filepath = os.path.abspath(self.file.path).replace(
                f"{ext}", f"{suffix}{ext}"
            )
        except IndexError:
            preview_filepath = os.path.abspath(self.file.path) + suffix
        preview_filename = os.path.basename(preview_filepath)

        img = PIL_Image.open(self.file.path)
        img = img.resize((300, 300), PIL_Image.LANCZOS)
        img.save(preview_filepath, "PNG")

        with open(preview_filepath, "rb") as f:
            self.preview.save(preview_filename, ContentFile(f.read()))
        self.save(update_fields=["preview"])

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
