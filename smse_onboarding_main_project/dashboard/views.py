from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from tasks.models import Task, TaskProgress
from users.models import Faculty
from documents.models import FacultyDocument
from django.utils import timezone
from django.http import JsonResponse

def get_faculty_from_request(request):
    """Helper function to get faculty profile from request"""
    if request.user.is_authenticated:
        try:
            return request.user.faculty_profile
        except AttributeError:
            pass
    return None

def is_admin(user):
    """Check if user is admin"""
    if user.is_superuser:
        return True
    try:
        return user.is_authenticated and user.faculty_profile.is_admin
    except:
        return False

@login_required
def new_hire_home(request):
    """Render the new hire dashboard home page"""
    faculty = get_faculty_from_request(request)
    if not faculty:
        if request.user.is_superuser:
            return redirect('dashboard:admin_home')
        return redirect('users:login')

    tasks = Task.objects.all()
    documents = FacultyDocument.objects.filter(faculty=faculty)

    # Get all tasks assigned to this faculty
    assigned_tasks = tasks.filter(assigned_to=faculty)
    total_assigned_tasks = assigned_tasks.count()

    # Get completed tasks for this faculty
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

    # Add completion status to each task
    for task in tasks:
        task.is_completed_by_faculty = task.id in completed_task_ids
        print(f"DEBUG: Task {task.id} - {task.title} - Completed: {task.is_completed_by_faculty}")

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

    return render(request, 'dashboard/new_hire/home.html', context)

@login_required
@user_passes_test(is_admin)
def admin_home(request):
    """
    Admin dashboard view showing upcoming deadlines and admin tasks
    """
    # Get all faculty members who haven't completed onboarding
    faculty_members = Faculty.objects.filter(completed_onboarding=False)
    faculty_tasks = []

    for faculty in faculty_members:
        assigned_tasks = Task.objects.filter(assigned_to=faculty)
        total_tasks = assigned_tasks.count()

        completed_tasks = TaskProgress.objects.filter(
            faculty=faculty,
            completed=True,
            task__in=assigned_tasks
        ).count()

        completion_percentage = 0
        if total_tasks > 0:
            completion_percentage = (completed_tasks / total_tasks) * 100

        next_task = Task.objects.filter(
            assigned_to=faculty
        ).exclude(
            id__in=TaskProgress.objects.filter(
                faculty=faculty,
                completed=True
            ).values_list('task_id', flat=True)
        ).order_by('deadline').first()

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

    # admin tasks definition
    now = timezone.now()
    admin_tasks = [
        {
            'id': 1,
            'title': 'Contract Written',
            'description': 'Make sure to have the new hire contract written.',
            'assigned_to': 'admin Person',
            'deadline': now + timezone.timedelta(days=30),
            'completed': False,
            'is_overdue': False
        },
        {
            'id': 2,
            'title': 'Office Assignment',
            'description': 'Assign new hire for there office.',
            'assigned_to': 'admin Person',
            'deadline': now + timezone.timedelta(days=-5),  # 5 days overdue
            'completed': False,
            'is_overdue': True
        },
        {
            'id': 3,
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

@login_required
def complete_task(request, task_id):
    """Mark a task as completed for the current faculty."""
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

                # For AJAX requests, return JSON response with updated data
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # Count total and completed tasks
                    assigned_tasks = Task.objects.filter(assigned_to=faculty)
                    total_tasks = assigned_tasks.count()
                    completed_tasks = TaskProgress.objects.filter(
                        faculty=faculty,
                        completed=True,
                        task__in=assigned_tasks
                    ).count()
                    
                    return JsonResponse({
                        'success': True,
                        'completed': True,
                        'task_id': task_id,
                        'completed_count': completed_tasks,
                        'total_count': total_tasks
                    })
                
                # For regular requests, redirect
                return redirect('dashboard:new_hire_home')

        except Task.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
            pass

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
    return redirect('dashboard:new_hire_home')

@login_required
def continue_task(request, task_id):
    """Mark a task as not completed for the current faculty."""
    if request.method == 'POST':
        try:
            task = Task.objects.get(pk=task_id)
            faculty = get_faculty_from_request(request)

            if faculty:
                # Delete the task progress (mark as incomplete)
                deleted_count = TaskProgress.objects.filter(
                    faculty=faculty,
                    task=task
                ).delete()[0]
                
                # For AJAX requests, return JSON response with updated data
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # Count total and completed tasks
                    assigned_tasks = Task.objects.filter(assigned_to=faculty)
                    total_tasks = assigned_tasks.count()
                    completed_tasks = TaskProgress.objects.filter(
                        faculty=faculty,
                        completed=True,
                        task__in=assigned_tasks
                    ).count()
                    
                    return JsonResponse({
                        'success': True,
                        'completed': False,
                        'task_id': task_id,
                        'completed_count': completed_tasks,
                        'total_count': total_tasks
                    })
                
                # For regular requests, redirect
                return redirect('dashboard:new_hire_home')

        except Task.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
            pass
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            pass

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
    return redirect('dashboard:new_hire_home')
