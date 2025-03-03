from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from tasks.models import Task, Faculty, TaskProgress
from django.urls import reverse
import json

def get_faculty_from_request(request):
    """
    Helper function to get the faculty object from the request.
    """
    if request.user.is_authenticated:
        try:
            # Assuming user is linked to faculty
            return request.user.faculty_profile
        except AttributeError:
            pass
    return None

def home(request):
    """
    Render the home page with a list of tasks.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    faculty = get_faculty_from_request(request)
    if not faculty:
        return redirect('login')
        
    tasks = Task.objects.all()
    
    # Get all completed tasks for this faculty in one database query
    completed_task_ids = set(
        TaskProgress.objects.filter(
            faculty=faculty,
            completed=True
        ).values_list('task_id', flat=True)
    )
    
    # Calculate days remaining and set completion status for each task
    for task in tasks:
        # Add faculty-specific completion status
        task.is_completed_by_faculty = task.id in completed_task_ids
    
    context = {
        'tasks': tasks,
        'faculty': faculty,
    }
    
    return render(request, 'new_hire_dashboard/home.html', context)

def complete_task(request, task_id):
    """
    Mark a task as completed for the current faculty.
    """
    if request.method == 'POST':
        try:
            task = Task.objects.get(pk=task_id)
            faculty = get_faculty_from_request(request)
            
            if faculty:
                # Mark task as completed for this specific faculty
                TaskProgress.objects.update_or_create(
                    faculty=faculty,
                    task=task,
                    defaults={'completed': True}
                )
                
                # Check if all faculty have completed this task
                assigned_faculty_count = task.assigned_to.count()
                completed_faculty_count = TaskProgress.objects.filter(
                    task=task,
                    faculty__in=task.assigned_to.all(),
                    completed=True
                ).count()
                
                # Only update the task's completed status if all assigned faculty have completed it
                if completed_faculty_count == assigned_faculty_count and not task.completed:
                    task.completed = True
                    task.save()
                
                return redirect('tasks:home')
            
        except Task.DoesNotExist:
            pass
    
    return redirect('tasks:home')

def continue_task(request, task_id):
    """
    Mark a task as not completed for the current faculty.
    """
    if request.method == 'POST':
        try:
            task = Task.objects.get(pk=task_id)
            faculty = get_faculty_from_request(request)
            
            if faculty:
                # Mark task as not completed for this specific faculty
                TaskProgress.objects.filter(
                    faculty=faculty,
                    task=task
                ).delete()
                
                # Update the task's completed status
                if task.completed:
                    task.completed = False
                    task.save()
                
                return redirect('tasks:home')
            
        except Task.DoesNotExist:
            pass
    
    return redirect('tasks:home')

def admin_help(request):
    return render(request, 'new_hire_dashboard/admin_resources/admin_help.html')