from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Task


def home(request):
    #return HttpResponse("Hello world. You're at the dashboard.")
    # Task.objects.create(
    #     title = "Get Zoom phone",
    #     description = "Get a Zoom phone number.",
    #     created_at = "2024-12-02 18:07",
    #     completed = True,
    #     deadline = "2025-01-05 23:59",
    # )
    tasks = Task.objects.all()
    return render(request, 'new_hire_dashboard/home.html', {"tasks": tasks})

def notifications(request):
    #return HttpResponse("Hello world. You're at the dashboard.")
    return render(request, 'new_hire_dashboard/notifications.html')