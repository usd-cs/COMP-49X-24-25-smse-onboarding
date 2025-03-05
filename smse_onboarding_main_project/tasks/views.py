from django.http import JsonResponse, FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from tasks.models import Task, Faculty, FacultyDocument, TaskProgress
import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.db import models
from django.conf import settings
import os
from django.contrib.auth import authenticate, login

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
        'documents': documents,  # Add documents to context
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
    """
    View for the help guide page
    """
    return render(request, 'tasks/help_guide.html')

@login_required
def show_documents(request, faculty_id=None):
    """Shows the list of all faculty documents"""
    user = request.user

    if faculty_id:
        faculty = get_object_or_404(Faculty, faculty_id=faculty_id)
        if not user.is_staff and (not hasattr(user, 'faculty_profile') or user.faculty_profile.faculty_id != faculty_id):
            raise PermissionDenied
        documents = FacultyDocument.objects.filter(faculty=faculty)
    else:
        if user.is_staff:
            documents = FacultyDocument.objects.all()
        else:
            faculty = get_object_or_404(Faculty, user=user)
            documents = FacultyDocument.objects.filter(faculty=faculty)

    return render(request, 'tasks/document_list.html', {
        'documents': documents,
        'faculty': faculty if faculty_id else None
    })

@login_required
def upload_document(request):
    """View for uploading documents"""
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty')

        if not request.user.is_staff:
            faculty = get_object_or_404(Faculty, user=request.user)
            if str(faculty.faculty_id) != faculty_id:
                raise PermissionDenied

        document = FacultyDocument(
            faculty_id=faculty_id,
            title=request.POST.get('title'),
            file=request.FILES['document'],
            uploaded_by=request.user
        )
        document.save()
        messages.success(request, 'Document uploaded successfully!')
        return redirect('tasks:home')

    return redirect('tasks:home')

@login_required
def delete_document(request, doc_id):
    """View for deleting documents"""
    if request.method == 'POST':  # Change to POST for security reasons
        document = get_object_or_404(FacultyDocument, document_id=doc_id)

        # Check permissions
        if not request.user.is_staff and (not hasattr(request.user, 'faculty_profile') or
                                         request.user.faculty_profile != document.faculty):
            raise PermissionDenied

        document.delete()
        messages.success(request, 'Document deleted successfully!')
    return redirect('tasks:home')

@login_required
def download_document(request, doc_id):
    """View for downloading documents"""
    document = get_object_or_404(FacultyDocument, document_id=doc_id)

    # Check permissions
    if not request.user.is_staff and (not hasattr(request.user, 'faculty_profile') or
                                     request.user.faculty_profile != document.faculty):
        raise PermissionDenied

    file_path = os.path.join(settings.MEDIA_ROOT, document.file.name)
    if os.path.exists(file_path):
        # Get file extension and actual MIME type
        file_ext = os.path.splitext(document.file.name)[1].lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        content_type = content_types.get(file_ext, 'application/octet-stream')

        # Use the actual filename from storage
        filename = os.path.basename(document.file.name)

        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        messages.error(request, 'File not found.')
        return redirect('tasks:home')

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

    faculty_tasks = [
        {
            'id': 1,
            'name': 'Harley Quinn',
            'current_task': 'Request computer',
            'completion_percentage': 50,
            'status_class': 'approaching',
            'remaining_days': -94,
            'all_tasks': []
        },
        {
            'id': 2,
            'name': 'Bruce Wayne',
            'current_task': 'Request office key',
            'completion_percentage': 60,
            'status_class': 'upcoming',
            'remaining_days': -90,
            'all_tasks': []
        },
        {
            'id': 3,
            'name': 'Clark Kent',
            'current_task': 'Request mailbox',
            'completion_percentage': 20,
            'status_class': 'overdue',
            'remaining_days': -90,
            'all_tasks': []
        },
        {
            'id': 4,
            'name': 'Diana Prince',
            'current_task': 'Complete Security Training',
            'completion_percentage': 100,
            'status_class': 'completed',
            'remaining_days': -71,
            'all_tasks': []
        }
    ]

    admin_tasks = [
        {
            'title': 'Send Welcome Gift',
            'assigned_to': 'Clark Kent',
            'deadline': timezone.now() + timezone.timedelta(days=30),
            'completed': False
        },
        {
            'title': 'Assign Office',
            'assigned_to': 'Clark Kent',
            'deadline': timezone.now() + timezone.timedelta(days=45),
            'completed': False
        },
        {
            'title': 'Task 3',
            'assigned_to': 'Bruce Wayne',
            'deadline': timezone.now() + timezone.timedelta(days=60),
            'completed': True
        }
    ]

    context = {
        'faculty_tasks': faculty_tasks,
        'admin_tasks': admin_tasks,
    }

    return render(request, 'admin_dashboard/admin_dashboard.html', context)

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if is_admin(user):
                return redirect('admin_dashboard')
            else:
                return redirect('tasks:home')

    return render(request, 'login/login.html')
