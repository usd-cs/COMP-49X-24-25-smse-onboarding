from django.http import JsonResponse, FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.conf import settings
import os

# Import models properly
from .models import Task, Faculty, TaskProgress
from documents.models import FacultyDocument

def get_faculty_from_request(request):
    """
    Helper function to get the faculty object from the request.
    """
    if request.user.is_authenticated:
        try:
            return request.user.faculty_profile
        except AttributeError:
            pass
    return None

@login_required
def home(request):
    """
    Render the home page with tasks and documents data
    """
    faculty = get_faculty_from_request(request)
    if not faculty:
        if request.user.is_superuser:
            return redirect('admin_dashboard')

        return redirect('login')

    tasks = Task.objects.all()
    documents = FacultyDocument.objects.filter(faculty=faculty)

    # Get all tasks assigned to this faculty
    assigned_tasks = tasks.filter(assigned_to=faculty)
    total_assigned_tasks = assigned_tasks.count()

    # Get all completed tasks for this faculty in one database query
    completed_task_ids = set(
        TaskProgress.objects.filter(
            faculty=faculty,
            completed=True
        ).values_list('task_id', flat=True)
    )

    # Count completed tasks
    completed_tasks_count = len(completed_task_ids)

    # Calculate completion percentage
    completion_percentage = 0
    if total_assigned_tasks > 0:
        completion_percentage = (completed_tasks_count / total_assigned_tasks) * 100

    # Calculate days remaining and set completion status for each task
    for task in tasks:
        # Add faculty-specific completion status
        task.is_completed_by_faculty = task.id in completed_task_ids

    context = {
        'tasks': tasks,
        'faculty': faculty,
        'documents': documents,
        'show_documents': True,
        'completed_tasks_count': completed_tasks_count,
        'total_assigned_tasks': total_assigned_tasks,
        'completion_percentage': round(completion_percentage),
        'num_completed': completed_tasks_count,
        'num_tasks': total_assigned_tasks,
        'percentage': round(completion_percentage),
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

            if faculty and task.is_unlocked():
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

                # Use the correct URL pattern name with namespace
                return redirect('tasks:home')

        except Task.DoesNotExist:
            pass

    # Use the correct URL pattern name with namespace
    return redirect('tasks:home')

@login_required
def help_guide(request):
    """View for the help guide page"""
    context = {
        'user': request.user,
    }
    return render(request, 'tasks/help_guide.html', context)

def is_admin(user):
    """
    Check if the user is an admin or a superuser.
    """
    if user.is_superuser:
        return True
    try:
        return user.is_authenticated and user.faculty_profile.is_admin
    except:
        return False

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    Admin dashboard view showing upcoming deadlines and admin tasks
    """
    # Get all faculty members who haven't completed onboarding
    faculty_members = Faculty.objects.filter(completed_onboarding=False)
    faculty_tasks = []

    for faculty in faculty_members:
        # Get all tasks assigned to this faculty
        assigned_tasks = Task.objects.filter(assigned_to=faculty)
        total_tasks = assigned_tasks.count()

        # Get completed tasks for this faculty
        completed_tasks = TaskProgress.objects.filter(
            faculty=faculty,
            completed=True,
            task__in=assigned_tasks
        ).count()

        # Calculate completion percentage
        completion_percentage = 0
        if total_tasks > 0:
            completion_percentage = (completed_tasks / total_tasks) * 100

        # Get the next incomplete task
        next_task = Task.objects.filter(
            assigned_to=faculty
        ).exclude(
            id__in=TaskProgress.objects.filter(
                faculty=faculty,
                completed=True
            ).values_list('task_id', flat=True)
        ).order_by('deadline').first()

        # Determine status class based on completion and deadlines
        status_class = 'upcoming'
        if completion_percentage == 100:
            status_class = 'completed'
        elif next_task and next_task.deadline < timezone.now():
            status_class = 'overdue'
        elif next_task and (next_task.deadline - timezone.now()).days < 7:
            status_class = 'approaching'

        faculty_tasks.append({
            'id': faculty.faculty_id,
            'name': f"{faculty.first_name} {faculty.last_name}",
            'current_task': next_task.title if next_task else "All tasks completed",
            'completion_percentage': round(completion_percentage),
            'status_class': status_class,
            'remaining_days': (next_task.deadline - timezone.now()).days if next_task else 0,
            'all_tasks': [
                {
                    'title': task.title,
                    'completed': TaskProgress.objects.filter(faculty=faculty, task=task, completed=True).exists(),
                    'deadline': task.deadline
                } for task in assigned_tasks
            ]
        })

    # Get admin tasks (tasks that need admin attention)
    now = timezone.now()
    admin_tasks = [
        {
            'id': 1,  # 添加 ID 字段
            'title': 'Contract Written',
            'description': 'Make sure to have the new hire contract written.',
            'assigned_to': 'admin Person',
            'deadline': now + timezone.timedelta(days=30),
            'completed': False,
            'is_overdue': False
        },
        {
            'id': 2,  # 添加 ID 字段
            'title': 'Office Assignment',
            'description': 'Assign new hire for there office.',
            'assigned_to': 'admin Person',
            'deadline': now + timezone.timedelta(days=-5),  # 5 days overdue
            'completed': False,
            'is_overdue': True
        },
        {
            'id': 3,  # 添加 ID 字段
            'title': 'Collect CVs',
            'description': 'Collecting recent new hires\' CVs and Bios.',
            'assigned_to': 'admin Person',
            'deadline': now + timezone.timedelta(days=60),
            'completed': True,
            'is_overdue': False
        }
    ]

    context = {
        'faculty_tasks': faculty_tasks,
        'admin_tasks': admin_tasks,
    }

    return render(request, 'admin_dashboard/admin_dashboard.html', context)

def custom_login(request):
    return render(request, 'login/login.html')

@login_required
@user_passes_test(is_admin)
def toggle_admin_task(request, task_id):
    """
    Toggle the completion status of an admin task
    """
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        faculty = get_faculty_from_request(request)

        if faculty:
            if task.is_completed_by(faculty):
                task.uncomplete_for_faculty(faculty)
                completed = False
            else:
                task.complete_for_faculty(faculty)
                completed = True

            return JsonResponse({
                'status': 'success',
                'completed': completed,
                'is_overdue': task.deadline < timezone.now()
            })

    return JsonResponse({'status': 'error'}, status=400)
