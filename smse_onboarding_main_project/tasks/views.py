from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from tasks.models import Task, Faculty
import json

def home(request):
    """
    Render the home page.
    Original comments preserved.
    """
    tasks = Task.objects.all()

    num_completed = 0

    # Loop through tasks to count completed tasks.
    for task in tasks:
        if task.completed:
            num_completed += 1

    total_tasks = len(tasks)
    percentage = (num_completed / total_tasks) * 100 if total_tasks > 0 else 0

    try:
        faculty = Faculty.objects.get(user=request.user)
    except Exception as e:
        faculty = None
        print('Exception : ', e)

    return render(request, 'new_hire_dashboard/home.html', {
        'faculty': faculty,
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
        
        if task.is_unlocked():
            task.completed = True  
            task.save()
        return redirect('tasks:home')
    
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
        task.completed = False  # mark task as incomplete
        task.save()
        return redirect('tasks:home')
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def admin_help(request):
    return render(request, 'tasks/help_guide.html')