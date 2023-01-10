from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

from people.core.models import Person


@login_required
@require_http_methods(("GET",))
def home(request):
    persons = Person.objects.filter(created_by=request.user)

    for person in persons:
        if not person.avatar.name:
            continue
        person.avatar_url = request.build_absolute_uri(person.avatar.url)

    return render(request, "core/home.html", {"persons": persons})


@login_required
@require_http_methods(("GET", "POST"))
def create_person(request):
    if request.method == "GET" and request.htmx:
        return render(request, "core/_create_person_dialog.html", {})

    elif request.method == "POST":
        Person.objects.get_or_create(
            first_name=request.POST["first_name"],
            last_name=request.POST["last_name"],
            created_by=request.user,
        )

    return redirect("home")


@login_required
@require_http_methods(("POST",))
def update_person(request, person_id: int):
    person = Person.objects.get(id=person_id)

    person.x = float(request.POST["x"])
    person.y = float(request.POST["y"])
    person.angle = float(request.POST["angle"])
    person.scale = float(request.POST["scale"])
    person.save()

    return HttpResponse()
