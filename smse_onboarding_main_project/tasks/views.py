from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Task


def home(request):
    # return HttpResponse("Hello world. You're at the dashboard.")
    # Task.objects.create(
    #     title = "Get Zoom phone",
    #     description = "Get a Zoom phone number.",
    #     created_at = "2024-12-02 18:07",
    #     completed = True,
    #     deadline = "2025-01-05 23:59",
    # )
    tasks = Task.objects.all()
    return render(request, 'new_hire_dashboard/home.html', {
        'tasks': tasks,
    })

def notifications(request):
    # return HttpResponse("Hello world. You're at the dashboard.")
    return render(request, 'new_hire_dashboard/notifications.html')

def complete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        task.completed = True  # mark complete
        task.save()
        return JsonResponse({'message': f'Task "{task.title}" marked as completed successfully!'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)
