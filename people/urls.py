from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from people.core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("persons/create", views.create_person, name="create-person"),
    path("persons/<int:person_id>", views.update_person, name="update-person"),
    path("", views.home, name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
