from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from people.core.models import User, Person, Image, PersonImage

admin.site.site_header = "The People Around You - Administration"


class CustomUserAdmin(UserAdmin):
    pass


class PersonAdmin(admin.ModelAdmin):
    list_display = ("label", "first_name", "last_name", "created_by", "avatar_preview")

    def label(self, person):
        created_by = person.created_by or "-"
        return f"{created_by}: {person.first_name} {person.last_name}"

    @mark_safe
    def avatar_preview(self, person):
        if not person.avatar.name:
            return ""
        return (
            f"<img src='{person.avatar.url}' height='240px'>"
            f"<br>"
            f"<small style='color: grey'>"
            f"  {person.avatar.width} x {person.avatar.height} px"
            f"</small>"
        )


admin.site.register(Image)
admin.site.register(Person, PersonAdmin)
admin.site.register(PersonImage)
admin.site.register(User, CustomUserAdmin)
