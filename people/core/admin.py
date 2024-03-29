from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from simple_history.admin import SimpleHistoryAdmin

from people.core.models import User, Person, Image, PersonImage

admin.site.site_header = "The People Around You - Administration"


class CustomUserAdmin(UserAdmin):
    pass


class PersonAdmin(SimpleHistoryAdmin):
    list_display = (
        "name",
        "date_of_birth",
        "date_of_death",
        "created_by",
        "avatar_preview",
    )
    search_fields = (
        "created_by__first_name",
        "created_by__last_name",
        "created_by__username",
        "date_of_birth",
        "date_of_death",
        "name",
    )

    @mark_safe
    def avatar_preview(self, person):
        if not person.avatar_url:
            return ""
        return f"<img src='{person.avatar_url}' height='240px'>"


class PersonImageAdmin(admin.ModelAdmin):
    list_display = ("person", "image", "image_preview", "created_at")
    autocomplete_fields = ("person", "image")

    @mark_safe
    def image_preview(self, person_image):
        if not person_image.image.preview.name:
            return ""
        return f"<img src='{person_image.image.preview.url}' height='120px'>"


class ImageAdmin(admin.ModelAdmin):
    list_display = ("file", "preview_preview", "created_at")
    search_fields = ("file", "created_at")

    @mark_safe
    def preview_preview(self, image):
        if not image.preview.name:
            return ""
        return f"<img src='{image.preview.url}' height='120px'>"


admin.site.register(Image, ImageAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(PersonImage, PersonImageAdmin)
admin.site.register(User, CustomUserAdmin)
