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
from .models import Task, TaskProgress
from users.models import Faculty
from documents.models import FacultyDocument

def get_faculty_from_request(request):
    """
    Helper function to get the faculty object from the request.
    """
    if request.user.is_authenticated:
        try:
            return Faculty.objects.get(user=request.user)
        except Faculty.DoesNotExist:
            return None
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
        return redirect('users:login')

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

    # Debug output
    print("DEBUG: Task Information")
    print(f"Faculty: {faculty.first_name} {faculty.last_name}")
    print(f"Total tasks: {tasks.count()}")
    print(f"Assigned tasks: {assigned_tasks.count()}")
    print(f"Completed tasks: {completed_tasks_count}")

    # Calculate days remaining and set completion status for each task
    for task in tasks:
        # Add faculty-specific completion status
        task.is_completed_by_faculty = task.id in completed_task_ids
        print(f"Task: {task.title} - Completed: {task.is_completed_by_faculty}")

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

    return render(request, 'tasks/new_hire_dashboard/home.html', context)

@login_required
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

@login_required
def show_documents(request):
    """Shows documents for the logged-in user"""
    user = request.user

    # Get documents uploaded by the current user
    if user.is_staff:
        documents = FacultyDocument.objects.filter(uploaded_by=user)
    else:
        faculty = get_object_or_404(Faculty, user=user)
        documents = FacultyDocument.objects.filter(faculty=faculty)

    template_name = 'tasks/admin_document_list.html' if user.is_staff else 'tasks/document_list.html'

    context = {
        'documents': documents,
        'user': user,
    }

    return render(request, template_name, context)

@login_required
def upload_document(request):
    """View for uploading documents"""
    if request.method == 'POST':
        try:
            # Check if user is staff or has permission for the faculty
            if request.user.is_staff:
                faculty = request.user.faculty_profile
            else:
                faculty = get_object_or_404(Faculty, user=request.user)
                # Add this check to prevent uploading for other faculty
                if 'faculty_id' in request.POST:
                    target_faculty = get_object_or_404(Faculty, id=request.POST['faculty_id'])
                    if faculty != target_faculty:
                        raise PermissionDenied

            document = FacultyDocument(
                faculty=faculty,
                title=request.POST.get('title'),
                file=request.FILES['document'],
                uploaded_by=request.user
            )
            document.save()
            messages.success(request, 'Document uploaded successfully!')

        except PermissionDenied:
            # Return 403 instead of redirecting
            return JsonResponse({'error': 'Permission denied'}, status=403)
        except Exception as e:
            messages.error(request, f'Error uploading document: {str(e)}')

        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect(f"{reverse('tasks:home')}?show_documents=true")

    if request.user.is_staff:
        return redirect('admin_dashboard')
    return redirect('tasks:home')

@login_required
def delete_document(request, doc_id):
    """View for deleting documents"""
    if request.method == 'POST':
        try:
            document = get_object_or_404(FacultyDocument, document_id=doc_id)

            # Check permissions - return 403 if not authorized
            if not request.user.is_staff and (not hasattr(request.user, 'faculty_profile') or
                                            request.user.faculty_profile != document.faculty):
                return JsonResponse({'error': 'Permission denied'}, status=403)

            document.delete()
            messages.success(request, 'Document deleted successfully!')

            if request.user.is_staff:
                return redirect('admin_dashboard')
            return redirect(f"{reverse('tasks:home')}?show_documents=true")

        except Exception as e:
            messages.error(request, f'Error deleting document: {str(e)}')
            return JsonResponse({'error': str(e)}, status=400)

    if request.user.is_staff:
        return redirect('admin_dashboard')
    return redirect(f"{reverse('tasks:home')}?show_documents=true")

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

    return render(request, 'dashboard/admin/home.html', context)

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
