from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from PIL import Image

from people.core.models import Person, Image, PersonImage


FALLBACK_AVATAR_URL = "https://i.imgur.com/cGonva6.png"


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ("first_name", "last_name", "date_of_birth")


@login_required
@require_http_methods(("POST",))
def create_person(request):
    form = PersonForm(request.POST)
    form.is_valid()

    person = form.save(commit=False)
    person.created_by = request.user
    person.save()

    return JsonResponse(_serialize_person(person))


@login_required
@require_http_methods(("POST",))
def update_person(request, person_id: int):
    person = Person.objects.get(id=person_id, created_by=request.user)
    form = PersonForm(request.POST, instance=person)
    form.is_valid()
    form.save()
    person.refresh_from_db()
    return JsonResponse(_serialize_person(person))


def _serialize_person(person: Person) -> dict:
    x = {
        "avatar": person.avatar_url or FALLBACK_AVATAR_URL,
        "date_of_birth": (
            None if not person.date_of_birth else person.date_of_birth.isoformat()
        ),
        "first_name": person.first_name,
        "id": person.id,
        "image": None,
        "last_name": person.last_name,
        "scale": person.scale,
        "x": person.x,
        "y": person.y,
    }
    print("x", x)
    return x


@login_required
@require_http_methods(("POST",))
def update_person_transforms(request, person_id: int):
    person = Person.objects.get(id=person_id)

    person.x = float(request.POST["x"])
    person.y = float(request.POST["y"])
    person.scale = float(request.POST["scale"])
    person.save(update_fields=["x", "y", "scale"])

    return HttpResponse()


@login_required
@require_http_methods(("POST",))
def upload_avatar(request, person_id: int):
    person = Person.objects.get(id=person_id)
    avatar_file = request.FILES["avatar"]

    image = Image.objects.create(file=avatar_file)
    PersonImage.objects.create(person=person, image=image)

    person.refresh_from_db()
    return JsonResponse(_serialize_person(person))


@login_required
@require_http_methods(("POST",))
def delete_person(request, person_id: int):
    person = Person.objects.get(id=person_id)
    assert person.created_by == request.user
    person.delete()
    return redirect("home")


@login_required
@require_http_methods(("GET",))
def list_persons(request):
    persons = Person.objects.filter(created_by=request.user)
    return JsonResponse([_serialize_person(person) for person in persons], safe=False)
