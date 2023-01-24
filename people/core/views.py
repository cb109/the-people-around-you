import os
from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from people.core.models import Person


FALLBACK_AVATAR_URL = "https://i.imgur.com/cGonva6.png"


def _get_absolute_avatar_url(request, person):
    if not person.avatar.name:
        return FALLBACK_AVATAR_URL
    return request.build_absolute_uri(person.avatar.url)


def _get_renderable_persons(request, persons=None):
    if not persons:
        persons = Person.objects.filter(created_by=request.user)
    for person in persons:
        person.avatar = _get_absolute_avatar_url(request, person)
    return persons


@login_required
@require_http_methods(("GET",))
def home(request):
    persons = _get_renderable_persons(request)
    return render(request, "core/home.html", {"persons": persons})


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = (
            "first_name",
            "last_name",
            # "avatar",
        )


@login_required
@require_http_methods(("POST",))
def create_person(request):
    from pprint import pprint

    pprint(request.POST)
    pprint(request.FILES)

    form = PersonForm(request.POST)
    person = form.save(commit=False)

    # avatar_file = request.FILES["avatar"]
    # avatar_filepath = os.path.join(settings.MEDIA_ROOT, "avatars", avatar_file.name)
    # with open(avatar_filepath) as f:
    #     f.write(avatar_file)
    # person.avatar = avatar_filepath

    person.created_by = request.user
    person.save()

    return JsonResponse(
        {
            "avatar": _get_absolute_avatar_url(request, person),
            "first_name": person.first_name,
            "id": person.id,
            "image": None,
            "last_name": person.last_name,
            "scale": person.scale,
            "x": person.x,
            "y": person.y,
        }
    )


@login_required
@require_http_methods(("POST",))
def update_person(request, person_id: int):
    person = Person.objects.get(id=person_id)

    person.x = float(request.POST["x"])
    person.y = float(request.POST["y"])
    person.scale = float(request.POST["scale"])
    person.save()

    return HttpResponse()


@login_required
@require_http_methods(("POST",))
def delete_person(request, person_id: int):
    person = Person.objects.get(id=person_id)
    assert person.created_by == request.user
    person.delete()
    return redirect("home")
