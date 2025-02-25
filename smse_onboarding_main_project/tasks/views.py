from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from tasks.models import Task, Faculty, TaskProgress
import json

def home(request):
    """
    Render the home page.
    Original comments preserved.
    """
    # Get the user logging in
    try:
        faculty = Faculty.objects.get(user=request.user)
    except Exception as e:
        faculty = None
        print('Exception : ', e)

    tasks = Task.objects.all()

    num_completed = 0
    total_tasks = 0

    # Loop through tasks to count completed tasks.
    for task in tasks:
        if faculty in task.assigned_to.all():
            total_tasks += 1
            task_progress = TaskProgress.objects.filter(task=task, faculty=faculty, completed=True).exists()

            if task_progress:
                num_completed += 1

    percentage = (num_completed / total_tasks) * 100 if total_tasks > 0 else 0

    return render(request, 'new_hire_dashboard/home.html', {
        'faculty': faculty,
        'tasks': tasks,
        'num_tasks': total_tasks,
        'num_completed': num_completed,
        'percentage': percentage
    })

def complete_task(request, task_id):
    """
    Marks a task complete for a specific faculty member

    Args:
        request: Request generated when user clicks to complete a task.
        task_id: The ID for the task.
    """
    if request.method == 'POST':
        faculty = request.user.faculty_profile

        """
        task = get_object_or_404(Task, id=task_id)
        
        task_progrsss
        if task.is_unlocked():
            task.completed = True  
            task.save()
        return redirect('tasks:home')
        """
        task_progress = get_object_or_404 (TaskProgress, task_id=task_id, faculty=faculty)

        task_progress.completed = True  #makes complete for specific faculty
        task_progress.save()
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

        """
        task = get_object_or_404(Task, id=task_id)
        task.completed = False  # mark task as incomplete
        task.save()
        return redirect('tasks:home')
        """
        faculty = request.user.faculty_profile  # Ensure the user is a faculty member
        task_progress = get_object_or_404(TaskProgress, task_id=task_id, faculty=faculty)

        task_progress.completed = False  #makes sure task resets
        task_progress.save()

        return redirect('tasks:home')

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def admin_help(request):
    return render(request, 'tasks/help_guide.html')
