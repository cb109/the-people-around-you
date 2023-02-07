import os
import random
import string
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from PIL import Image

from people.core.models import Person


FALLBACK_AVATAR_URL = "https://i.imgur.com/cGonva6.png"


def _get_random_string(length: int) -> str:
    return "".join(random.choice(string.ascii_lowercase) for _ in range(length))


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ("first_name", "last_name")


@login_required
@require_http_methods(("POST",))
def create_person(request):
    form = PersonForm(request.POST)
    person = form.save(commit=False)

    prefix = _get_random_string(10)
    avatar_file = request.FILES["avatar"]
    avatar_filename = request.POST["avatar_filename"]
    avatar_filepath = os.path.join(
        settings.MEDIA_ROOT,
        "avatars",
        f"{prefix}.{avatar_filename}",
    )
    try:
        os.makedirs(os.path.dirname(avatar_filepath))
    except FileExistsError:
        pass
    with open(avatar_filepath, "wb") as f:
        f.write(avatar_file.read())

    # Create normalized size version.
    normalized_filepath = avatar_filepath + "_300x300.png"
    img = Image.open(avatar_filepath)
    img = img.resize((300, 300), Image.LANCZOS)
    img.save(normalized_filepath, "PNG")

    # media_relative_filepath = os.path.join(
    #     "avatars", os.path.basename(normalized_filepath)
    # )
    with open(normalized_filepath, "rb") as f:
        person.avatar = File(f, name=f.name)

    person.created_by = request.user
    person.save()

    return JsonResponse(_serialize_person(request, person))


def _serialize_person(request, person: Person) -> dict:
    return {
        "avatar": person.avatar.url if person.avatar.name else FALLBACK_AVATAR_URL,
        "first_name": person.first_name,
        "id": person.id,
        "image": None,
        "last_name": person.last_name,
        "scale": person.scale,
        "x": person.x,
        "y": person.y,
    }


@login_required
@require_http_methods(("POST",))
def update_person(request, person_id: int):
    person = Person.objects.get(id=person_id)

    person.x = float(request.POST["x"])
    person.y = float(request.POST["y"])
    person.scale = float(request.POST["scale"])
    person.save(update_fields=["x", "y", "scale"])

    return HttpResponse()


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
    return JsonResponse(
        [_serialize_person(request, person) for person in persons], safe=False
    )