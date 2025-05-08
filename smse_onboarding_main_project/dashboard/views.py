from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from tasks.models import Task, TaskProgress
from users.models import Faculty
from documents.models import FacultyDocument
from reminders.models import Reminder
from reminders.views import send_reminder_admin
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from datetime import datetime
import logging
from django import forms
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)

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
    if user.is_superuser or user.is_staff:
        return True
    try:
        return user.is_authenticated and user.faculty_profile.is_admin
    except:
        return False

@login_required
def new_hire_home(request):
    """Render the new hire dashboard home page"""
    logger.debug(f"New hire home view - User: {request.user.email}, Session: {request.session.get('show_welcome_banner')}")

    # Check if user is staff or admin, redirect to admin dashboard if so
    if request.user.is_staff or is_admin(request.user):
        return redirect('dashboard:admin_home')

    faculty = get_faculty_from_request(request)
    if not faculty:
        if request.user.is_superuser:
            return redirect('dashboard:admin_home')
        return redirect('users:login')

    # Get all tasks assigned to this faculty
    tasks = Task.objects.filter(assigned_to=faculty)
    documents = FacultyDocument.objects.filter(faculty=faculty)
    unread_reminders_count = Reminder.objects.filter(
        faculty=faculty,
        is_read=False
    ).count()

    # Get completed tasks for this faculty
    completed_task_ids = set(
        TaskProgress.objects.filter(
            faculty=faculty,
            completed=True
        ).values_list('task_id', flat=True)
    )

    # Add completion status and prerequisite info to each task
    for task in tasks:
        task.is_completed_by_faculty = task.id in completed_task_ids
        # Check prerequisite task status
        if task.prerequisite_task:
            task.prereq_completed = task.prerequisite_task.id in completed_task_ids
            task.can_complete = task.prereq_completed and not task.is_completed_by_faculty
        else:
            task.prereq_completed = True
            task.can_complete = not task.is_completed_by_faculty

    # Separate tasks into upcoming and completed
    completed_tasks = [task for task in tasks if task.is_completed_by_faculty]
    upcoming_tasks = [task for task in tasks if not task.is_completed_by_faculty]

    # Count tasks
    total_assigned_tasks = len(tasks)
    completed_tasks_count = len(completed_tasks)

    # Calculate completion percentage
    completion_percentage = 0
    if total_assigned_tasks > 0:
        completion_percentage = (completed_tasks_count / total_assigned_tasks) * 100

    context = {
        'upcoming_tasks': upcoming_tasks,
        'completed_tasks': completed_tasks,
        'faculty': faculty,
        'documents': documents,
        'show_documents': True,
        'completed_tasks_count': completed_tasks_count,
        'total_assigned_tasks': total_assigned_tasks,
        'completion_percentage': round(completion_percentage),
        'num_completed': completed_tasks_count,
        'num_tasks': total_assigned_tasks,
        'percentage': round(completion_percentage),
        'unread_reminders_count': unread_reminders_count,
    }

    return render(request, 'dashboard/new_hire/home.html', context)

@login_required
@user_passes_test(is_admin)
def admin_home(request):
    """
    Admin dashboard view showing upcoming deadlines and admin tasks
    """
    logger.debug(f"Admin home view - User: {request.user.email}, Session: {request.session.get('show_welcome_banner')}")

    # Additional check for admin access - redirect to new_hire_home if not admin
    if not is_admin(request.user):
        return redirect('dashboard:new_hire_home')

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

        # Add additional faculty data
        faculty.department = faculty.engineering_dept
        faculty.start_date = faculty.hire_date
        faculty.extension = getattr(faculty, 'phone_extension', None)

        faculty_tasks.append({
            'id': faculty.faculty_id,
            'name': f"{faculty.first_name} {faculty.last_name}",
            'first_name': faculty.first_name,
            'last_name': faculty.last_name,
            'email': faculty.email,
            'department': faculty.department,
            'start_date': faculty.start_date,
            'extension': faculty.extension,
            'profile_image': faculty.profile_image,
            'completed_onboarding': faculty.completed_onboarding,
            'current_task': next_task if next_task else None,
            'current_task_title': next_task.title if next_task else "All tasks completed",
            'completion_percentage': 100 if not next_task else round(completion_percentage),
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

    for task in faculty_tasks:
        if task['current_task']:
            zero_reminders = Reminder.objects.filter(faculty=request.user.faculty_profile, secondary_faculty=task['id'], task=task['current_task'].id).count() == 0
            if (task['current_task'].deadline - timezone.now()).total_seconds() / 3600 <= 24 and (task['current_task'].deadline - timezone.now()).total_seconds() / 3600 > 0 and zero_reminders:
                send_reminder_admin(request, task['id'], task['current_task'].id, f"{task['name']} has less than 24 hours remaining to complete this task.")
            elif (task['current_task'].deadline - timezone.now()).total_seconds() / 3600 <= 0 and zero_reminders:
                send_reminder_admin(request, task['id'], task['current_task'].id, f"This task is overdue for {task['name']}.")

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

    unread_reminders_count = Reminder.objects.filter(
        faculty=request.user.faculty_profile,
        is_read=False
    ).count()

    admin = request.user.faculty_profile

    context = {
        'faculty_tasks': faculty_tasks,
        'admin_tasks': admin_tasks,
        'unread_reminders_count': unread_reminders_count,
        'admin': admin,
        'faculty': request.user.faculty_profile,
    }

    return render(request, 'dashboard/admin/home.html', context)

@login_required
def complete_task(request, task_id):
    """
    Mark a task as completed for the current faculty.
    """
    if request.method == 'POST':
        try:
            task = get_object_or_404(Task, pk=task_id)
            faculty = get_faculty_from_request(request)

            if faculty:
                # Check if prerequisite task is completed
                if task.prerequisite_task:
                    prereq_completed = TaskProgress.objects.filter(
                        faculty=faculty,
                        task=task.prerequisite_task,
                        completed=True
                    ).exists()
                    if not prereq_completed:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'status': 'error',
                                'message': 'Please complete the prerequisite task first'
                            }, status=400)
                        return redirect('dashboard:new_hire_home')

                # Mark task as completed for this specific faculty
                TaskProgress.objects.update_or_create(
                    faculty=faculty,
                    task=task,
                    defaults={'completed': True}
                )

                # 检查该 faculty 是否所有任务都完成，若是则设置 completed_onboarding = True
                assigned_tasks = Task.objects.filter(assigned_to=faculty)
                total_tasks = assigned_tasks.count()
                completed_tasks = TaskProgress.objects.filter(
                    faculty=faculty,
                    completed=True,
                    task__in=assigned_tasks
                ).count()
                if total_tasks > 0 and completed_tasks == total_tasks and not faculty.completed_onboarding:
                    faculty.completed_onboarding = True
                    faculty.save()

                # If AJAX request, return JSON response
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success'})

                return redirect('dashboard:new_hire_home')

        except Task.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Task not found'}, status=404)

    # If AJAX request but an error occurred
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'error'}, status=400)

    return redirect('dashboard:new_hire_home')

@login_required
def continue_task(request, task_id):
    """
    Mark a task as not completed for the current faculty.
    """
    if request.method == 'POST':
        try:
            task = get_object_or_404(Task, pk=task_id)
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

                # If AJAX request, return JSON response
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success'})

                return redirect('dashboard:new_hire_home')

        except Task.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Task not found'}, status=404)

    # If AJAX request but an error occurred
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'error'}, status=400)

    return redirect('dashboard:new_hire_home')

@login_required
def update_settings(request):
    """Update user settings"""
    if request.method == 'POST':
        faculty = get_faculty_from_request(request)
        if not faculty:
            return redirect('users:login')

        faculty.dark_mode = request.POST.get('dark_mode') == 'on'
        faculty.save()

        if is_admin(request.user):
            return redirect('dashboard:admin_home')

        return redirect('dashboard:new_hire_home')

@login_required
@user_passes_test(is_admin)
def faculty_directory(request):
    """
    View for displaying all faculty members in a directory format
    """
    # Get all faculty members
    faculty_members = Faculty.objects.all().order_by('first_name')

    # Format the faculty data for the template
    for faculty in faculty_members:
        faculty.department = faculty.engineering_dept
        faculty.start_date = faculty.hire_date
        faculty.extension = getattr(faculty, 'phone_extension', None)  # Add extension field

    unread_reminders_count = Reminder.objects.filter(
        faculty=request.user.faculty_profile,
        is_read=False
    ).count()

    admin = request.user.faculty_profile

    context = {
        'faculty_members': faculty_members,
        'is_admin': True,
        'unread_reminders_count': unread_reminders_count,
        'admin': admin,
    }

    return render(request, 'dashboard/admin/faculty_directory.html', context)

@login_required
@user_passes_test(is_admin)
def faculty_tasks(request, faculty_id):
    """API endpoint to get task data for a specific faculty member"""
    try:
        faculty = Faculty.objects.get(pk=faculty_id)

        # Get all tasks assigned to this faculty
        assigned_tasks = Task.objects.filter(assigned_to=faculty)

        # Get completed task progress records
        task_progress_records = TaskProgress.objects.filter(
            faculty=faculty,
            completed=True
        )

        # Create a set of completed task IDs for faster lookups
        completed_task_ids = set(task_progress_records.values_list('task_id', flat=True))

        # Format upcoming tasks
        upcoming_tasks = []
        for task in assigned_tasks.exclude(id__in=completed_task_ids):
            days_left = (task.deadline - timezone.now()).days
            if days_left < 0:
                days_text = "Overdue"
            elif days_left == 0:
                days_text = "Due today"
            elif days_left == 1:
                days_text = "1 day left"
            else:
                days_text = f"{days_left} days left"

            upcoming_tasks.append({
                'title': task.title,
                'due_date': task.deadline.strftime('%b %d, %Y'),
                'days_left': days_text,
                'description': task.description
            })

        # Format completed tasks
        completed_tasks = []
        for task in assigned_tasks.filter(id__in=completed_task_ids):
            try:
                task_progress = task_progress_records.get(task=task)

                # Use current date if completion_date is not available
                completion_date = getattr(task_progress, 'completion_date', timezone.now())

                completed_tasks.append({
                    'title': task.title,
                    'completed_date': completion_date.strftime('%b %d, %Y'),
                    'description': task.description
                })
            except TaskProgress.DoesNotExist:
                # Fallback if there's an issue with the task progress record
                completed_tasks.append({
                    'title': task.title,
                    'completed_date': 'Date unknown',
                    'description': task.description
                })

        return JsonResponse({
            'upcoming_tasks': upcoming_tasks,
            'completed_tasks': completed_tasks
        })
    except Faculty.DoesNotExist:
        return JsonResponse({'error': 'Faculty not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
def get_faculty(request, faculty_id):
    """API endpoint to get faculty information"""
    try:
        faculty = Faculty.objects.get(pk=faculty_id)
        data = {
            'first_name': faculty.first_name,
            'last_name': faculty.last_name,
            'date_of_birth': faculty.date_of_birth.strftime('%Y-%m-%d') if faculty.date_of_birth else '',
            'email': faculty.email,
            'engineering_dept': faculty.engineering_dept,
            'phone': faculty.phone,
            'zoom_phone': faculty.zoom_phone,
            'office_room': faculty.office_room,
            'hire_date': faculty.hire_date.strftime('%Y-%m-%d') if faculty.hire_date else '',
            'job_role': faculty.job_role,
            'bio': faculty.bio,
            'completed_onboarding': faculty.completed_onboarding,
        }
        return JsonResponse(data)
    except Faculty.DoesNotExist:
        return JsonResponse({'error': 'Faculty not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
def update_faculty(request, faculty_id):
    """API endpoint to update faculty information"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        faculty = Faculty.objects.get(pk=faculty_id)

        # Update faculty fields
        faculty.first_name = request.POST.get('first_name', faculty.first_name)
        faculty.last_name = request.POST.get('last_name', faculty.last_name)
        faculty.email = request.POST.get('email', faculty.email)
        faculty.engineering_dept = request.POST.get('engineering_dept', faculty.engineering_dept)
        faculty.phone = request.POST.get('phone', faculty.phone)
        faculty.zoom_phone = request.POST.get('zoom_phone', faculty.zoom_phone)
        faculty.office_room = request.POST.get('office_room', faculty.office_room)

        # Handle hire date
        hire_date = request.POST.get('hire_date')
        if hire_date:
            faculty.hire_date = datetime.strptime(hire_date, '%Y-%m-%d').date()

        # Handle date of birth
        date_of_birth = request.POST.get('date_of_birth')
        if date_of_birth:
            faculty.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()

        faculty.job_role = request.POST.get('job_role', faculty.job_role)
        faculty.bio = request.POST.get('bio', faculty.bio)
        faculty.completed_onboarding = request.POST.get('completed_onboarding') == 'on'

        faculty.save()

        return JsonResponse({'status': 'success'})
    except Faculty.DoesNotExist:
        return JsonResponse({'error': 'Faculty not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
def get_new_hire_deadlines(request):
    """API endpoint to get updated new hire deadlines data"""
    try:
        # Get all faculty members with pending tasks
        faculty_with_tasks = Faculty.objects.filter(completed_onboarding=False)

        deadlines_data = []
        for faculty in faculty_with_tasks:
            # Get the current task and its details
            current_task = Task.objects.filter(faculty=faculty, completed=False).order_by('due_date').first()

            if current_task:
                # Calculate progress
                total_tasks = Task.objects.filter(faculty=faculty).count()
                completed_tasks = Task.objects.filter(faculty=faculty, completed=True).count()
                progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

                # Calculate days overdue
                if current_task.due_date:
                    today = timezone.now().date()
                    days_overdue = (today - current_task.due_date).days if today > current_task.due_date else 0
                else:
                    days_overdue = 0

                deadlines_data.append({
                    'faculty_id': faculty.id,
                    'first_name': faculty.first_name,
                    'last_name': faculty.last_name,
                    'current_task': current_task.title,
                    'progress': progress,
                    'due_date': current_task.due_date.strftime('%Y-%m-%d') if current_task.due_date else None,
                    'days_overdue': days_overdue
                })

        return JsonResponse(deadlines_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
def get_user_permissions(request, faculty_id):
    """API endpoint to get user permissions"""
    try:
        faculty = Faculty.objects.get(pk=faculty_id)
        user = faculty.user

        data = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_admin': is_admin(user)
        }
        return JsonResponse(data)
    except Faculty.DoesNotExist:
        return JsonResponse({'error': 'Faculty not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
def update_user_permissions(request, user_id):
    """API endpoint to update user permissions"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(pk=user_id)

        # Update user permissions
        user.is_active = request.POST.get('is_active') == 'on'
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_superuser = request.POST.get('is_superuser') == 'on'

        # Handle role-based permissions
        if request.POST.get('userRole') == 'admin':
            user.is_staff = True
            try:
                faculty = user.faculty_profile
                faculty.is_admin = True
                faculty.save()
            except:
                pass
        else:
            try:
                faculty = user.faculty_profile
                faculty.is_admin = False
                faculty.save()
            except:
                pass

        user.save()

        return JsonResponse({'status': 'success'})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
@require_POST
def api_assign_tasks(request):
    user_id = request.POST.get('user_id')
    task_ids = request.POST.getlist('task_ids[]')
    if not user_id or not task_ids:
        return JsonResponse({'status': 'error', 'msg': 'User and tasks required'})
    try:
        faculty = Faculty.objects.get(pk=user_id)
        tasks = Task.objects.filter(id__in=task_ids)
        for task in tasks:
            task.assigned_to.add(faculty)
        return JsonResponse({'status': 'success'})
    except Faculty.DoesNotExist:
        return JsonResponse({'status': 'error', 'msg': 'User not found'})

@login_required
@user_passes_test(is_admin)
def task_management(request):
    faculty = get_faculty_from_request(request)
    unread_reminders_count = Reminder.objects.filter(faculty=faculty, is_read=False).count() if faculty else 0
    tasks = Task.objects.all().select_related('prerequisite_task')
    faculty_list = Faculty.objects.all()
    context = {
        'faculty': faculty,
        'unread_reminders_count': unread_reminders_count,
        'tasks': tasks,
        'faculty_list': faculty_list,
    }
    return render(request, 'dashboard/admin/task_management.html', context)

class TaskEditForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['description', 'prerequisite_task', 'deadline']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prerequisite_task': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

@login_required
@user_passes_test(is_admin)
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskEditForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('dashboard:task_management')
    else:
        form = TaskEditForm(instance=task)
    faculty = get_faculty_from_request(request)
    context = {
        'form': form,
        'task': task,
        'faculty': faculty,
    }
    return render(request, 'dashboard/admin/edit_task.html', context)

@login_required
@user_passes_test(is_admin)
@require_POST
def api_edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    description = request.POST.get('description', '').strip()
    prerequisite_id = request.POST.get('prerequisite_task')
    deadline_str = request.POST.get('deadline')
    if description:
        task.description = description
    if prerequisite_id == '' or prerequisite_id == 'None':
        task.prerequisite_task = None
    elif prerequisite_id:
        task.prerequisite_task = Task.objects.get(id=prerequisite_id)
    if deadline_str:
        try:
            task.deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        except Exception:
            pass
    task.save()
    return JsonResponse({'status': 'success'})

@login_required
@user_passes_test(is_admin)
@require_POST
def api_add_task(request):
    from tasks.models import Task
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    prerequisite_id = request.POST.get('prerequisite_task')
    deadline_str = request.POST.get('deadline')
    if not title:
        return JsonResponse({'status': 'error', 'msg': 'Title is required'})
    if not deadline_str:
        return JsonResponse({'status': 'error', 'msg': 'Deadline is required'})
    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
    except Exception:
        return JsonResponse({'status': 'error', 'msg': 'Invalid deadline format'})
    task = Task(title=title, description=description, deadline=deadline)
    if prerequisite_id:
        try:
            task.prerequisite_task = Task.objects.get(id=prerequisite_id)
        except Task.DoesNotExist:
            pass
    task.save()
    return JsonResponse({'status': 'success'})

@login_required
@user_passes_test(is_admin)
@require_POST
def api_delete_task(request, task_id):
    from tasks.models import Task
    try:
        Task.objects.get(id=task_id).delete()
        return JsonResponse({'status': 'success'})
    except Task.DoesNotExist:
        return JsonResponse({'status': 'error', 'msg': 'Task not found'})
