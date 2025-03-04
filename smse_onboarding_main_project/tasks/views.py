from django.http import JsonResponse, FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from tasks.models import Task, Faculty, FacultyDocument
import json
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.db import models
from django.conf import settings
import os

# The linter errors are wrong
# Django's model classes automatically get a Manager instance at .objects

@login_required
def home(request):
    """
    Render the home page with documents data for modals
    """
    try:
        faculty = Faculty.objects.get(user=request.user)
        # Get documents for the faculty
        documents = FacultyDocument.objects.filter(faculty=faculty)
    except Exception as e:
        faculty = None
        documents = []
        print('Exception : ', e)

    tasks = Task.objects.all()

    num_completed = 0
    total_tasks = 0

    # Loop through tasks to count completed tasks.
    for task in tasks:
        if faculty in task.assigned_to.all():
            total_tasks += 1
            if task.completed:
                num_completed += 1

    percentage = (num_completed / total_tasks) * 100 if total_tasks > 0 else 0

    return render(request, 'new_hire_dashboard/home.html', {
        'faculty': faculty,
        'tasks': tasks,
        'documents': documents,  # Add documents to context
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

@login_required
def show_documents(request, faculty_id=None):
    """Shows thel list of all faculty documents"""
    user = request.user

    # If faculty_id is provided, then can see pecific faculty's documents
    if faculty_id:
        faculty = get_object_or_404(Faculty, faculty_id=faculty_id)
        # Check permissions
        if not user.is_staff and (not hasattr(user, 'faculty_profile') or user.faculty_profile.faculty_id != faculty_id):
            raise PermissionDenied
        documents = FacultyDocument.objects.filter(faculty=faculty)
    else:
        # If user is staff, show all documents, otherwise show only their documents
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
