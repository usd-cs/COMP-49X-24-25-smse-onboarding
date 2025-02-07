from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task
import json

def home(request):
    """
    Render the home page.

    Args:
        request: Request generated when user clicks to go to the home page.
    """
    tasks = Task.objects.all()

    num_completed = 0

    # ensures remaining days is shown correctly
    for task in tasks:
        if not task.completed:
            task.remaining_days = (task.deadline - timezone.now()).days
        else:
            num_completed += 1

    # Avoid division by zero
    total_tasks = len(tasks)
    percentage = (num_completed / total_tasks) * 100 if total_tasks > 0 else 0

    return render(request, 'new_hire_dashboard/home.html', {
        'tasks': tasks, 
        'num_tasks': total_tasks, 
        'num_completed': num_completed, 
        'percentage': percentage
    })



def complete_task(request, task_id):
    """
    Backend function for completing a task.

    Args:
        request: Request generated when user clicks to complete a task.
        task_id: The ID for the task.
    """
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        task.completed = True  # mark complete
        task.save()
        return redirect('tasks:home')
        # return JsonResponse({'message': f'Task "{task.title}" marked as completed successfully!'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def continue_task(request, task_id):
    """
    Backend function for continuing a task.

    Args:
        request: Request generated when user clicks to continue a task.
        task_id: The ID for the task.
    """
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        task.completed = False  # mark complete
        task.save()
        return redirect('tasks:home')
        # return JsonResponse({'message': f'Task "{task.title}" marked as completed successfully!'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)
