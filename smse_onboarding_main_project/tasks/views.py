
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task


def home(request):

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
