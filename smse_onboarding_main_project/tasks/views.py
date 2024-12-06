import json

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from .models import Task


def home(request):
    # return HttpResponse("Hello world. You're at the dashboard.")

    # file = open('C:/Users/longp/Coding Projects/Python/Senior Project/COMP-49X-24-25-smse-onboarding/smse_onboarding_main_project/tasks/fixtures/test_data.json')
    # tasks_json = json.load(file)

    # for task in tasks_json:
    #     Task.objects.create(
    #         title = task['fields']['title'],
    #         description = task['fields']['description'],
    #         created_at = task['fields']['created_at'],
    #         completed = task['fields']['completed'],
    #         deadline = task['fields']['deadline'],
    #     )

    tasks = Task.objects.all()

    num_completed = 0

    # ensures remaining days is shown correctly
    for task in tasks:
        if not task.completed:
            task.remaining_days = (task.deadline - timezone.now()).days
        else:
            num_completed += 1

    return render(request, 'new_hire_dashboard/home.html', {
        'tasks': tasks, 'num_tasks': len(tasks), 'num_completed': num_completed, 'percentage': (num_completed / len(tasks)) * 100
    })

def complete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        task.completed = True  # mark complete
        task.save()
        return redirect('tasks:home')
        # return JsonResponse({'message': f'Task "{task.title}" marked as completed successfully!'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def continue_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        task.completed = False  # mark complete
        task.save()
        return redirect('tasks:home')
        # return JsonResponse({'message': f'Task "{task.title}" marked as completed successfully!'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)