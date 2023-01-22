import os
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from people.core.models import Person


def _get_renderable_persons(request, persons=None):
    if not persons:
        persons = Person.objects.filter(created_by=request.user)
    for person in persons:
        if not person.avatar.name:
            continue
        person.avatar = request.build_absolute_uri(person.avatar.url)
    return persons


@login_required
@require_http_methods(("GET",))
def home(request):
    persons = _get_renderable_persons(request)
    return render(request, "core/home.html", {"persons": persons})


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ("first_name", "last_name", "avatar")


@login_required
@require_http_methods(("GET", "POST"))
def create_person(request):
    from pprint import pprint

    pprint(request.POST)
    pprint(request.FILES)

    if request.method == "GET":
        return render(request, "core/_create_person_dialog.html", {})

    elif request.method == "POST":
        form = PersonForm(request.POST)
        if not form.is_valid():
            return render(
                request, "core/_create_person_dialog.html", {"error_form": form}
            )

        person = form.save(commit=False)

        avatar_file = request.FILES["avatar"]
        avatar_filepath = os.path.join(settings.MEDIA_ROOT, "avatars", avatar_file.name)
        with open(avatar_filepath) as f:
            f.write(avatar_file)
        person.avatar = avatar_filepath

        person.created_by = request.user
        person.save()

        persons = _get_renderable_persons(request, persons=[person])
        return render(request, "core/_create_person_dialog.html", {"persons": persons})

    return redirect("home")


@login_required
@require_http_methods(("POST",))
def update_person(request, person_id: int):
    person = Person.objects.get(id=person_id)

    person.x = float(request.POST["x"])
    person.y = float(request.POST["y"])
    # person.angle = float(request.POST["angle"])
    # person.scale = float(request.POST["scale"])
    person.save()

    return HttpResponse()


@login_required
@require_http_methods(("POST",))
def delete_person(request, person_id: int):
    person = Person.objects.get(id=person_id)
    assert person.created_by == request.user
    person.delete()
    return redirect("home")
