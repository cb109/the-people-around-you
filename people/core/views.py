from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from people.core.models import Person


@login_required
def home(request):
    persons = Person.objects.filter(created_by=request.user)
    return render(request, "home.html", {"persons": persons})
