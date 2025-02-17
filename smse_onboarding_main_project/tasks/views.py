from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from tasks.models import Task


def home(request):
    """
    Render the home page.

    Args:
        request: Request generated when user clicks to go to the home page.
    """
    tasks = Task.objects.all()

    num_completed = 0
    tasks_data = []

    # Setting the locking status of tasks
    for task in tasks:
        remaining_days = (task.deadline - timezone.now()).days if not task.completed else None
        if task.completed:
            num_completed += 1

        tasks_data.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "deadline": task.deadline,
            "remaining_days": remaining_days,
            "is_unlocked": task.is_unlocked(),  
        })

    # Avoid division by zero
    total_tasks = len(tasks)
    percentage = (num_completed / total_tasks) * 100 if total_tasks > 0 else 0

    return render(request, 'new_hire_dashboard/home.html', {
        'tasks': tasks_data, 
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


def complete_task(request, task_id):
    """
    Backend function for completing a task.

    Args:
        request: Request generated when user clicks to complete a task.
        task_id: The ID for the task.
    """
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)

        if not task.is_unlocked():
            return JsonResponse({'error': 'Task is locked and cannot be completed yet.'}, status=400)
        task.completed = True 
        task.save()
        return redirect('tasks:home')

    return JsonResponse({'error': 'Invalid request method'}, status=400)
