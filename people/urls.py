from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from people.core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # API
    path("api/persons/create", views.create_person, name="create-person"),
    path(
        "api/persons/<int:person_id>/transforms",
        views.update_person,
        name="update-person-transforms",
    ),
    path("api/persons/<int:person_id>", views.update_person, name="update-person"),
    path(
        "api/persons/<int:person_id>/delete", views.delete_person, name="delete-person"
    ),
    path("api/persons/", views.list_persons, name="list-persons"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
