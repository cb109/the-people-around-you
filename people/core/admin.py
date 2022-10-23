from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from people.core.models import User, Person

admin.site.site_header = "The People Around You - Administration"


class CustomUserAdmin(UserAdmin):
    pass


class PersonAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "avatar_preview")

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


admin.site.register(User, CustomUserAdmin)
admin.site.register(Person, PersonAdmin)
