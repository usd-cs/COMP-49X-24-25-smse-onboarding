from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from tasks.models import Task, TaskProgress
from users.models import Faculty, User
from documents.models import FacultyDocument
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from datetime import datetime
import logging
import uuid
from django.contrib.auth.models import Group
from django.views.decorators.http import require_http_methods
from django.db.utils import IntegrityError

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

        faculty_tasks.append({
            'id': faculty.faculty_id,
            'name': f"{faculty.first_name} {faculty.last_name}",
            'current_task': next_task if next_task else None,
            'current_task_title': next_task.title if next_task else "All tasks completed",
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
        faculty.profile_image = None  # We'll use initials instead
        faculty.extension = getattr(faculty, 'phone_extension', None)  # Add extension field
    
    context = {
        'faculty_members': faculty_members,
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
def add_faculty(request):
    """Handle adding a new faculty member"""
    if request.method == 'POST':
        try:
            # Get form data
            email = request.POST['email']
            username = request.POST['username']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            
            logger.info(f"Attempting to create faculty with email: {email}")
            
            # Debug: Check current state
            user_exists = User.objects.filter(username=username).exists()
            user_email_exists = User.objects.filter(email=email).exists()
            faculty_exists = Faculty.objects.filter(email=email).exists()
            
            logger.info(f"Current state - User exists: {user_exists}, User email exists: {user_email_exists}, Faculty exists: {faculty_exists}")
            
            # Check if user or faculty already exists
            if user_exists:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Username already exists',
                    'errors': {'username': ['This username is already taken.']}
                }, status=400)
            
            if user_email_exists:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email already exists',
                    'errors': {'email': ['This email address is already registered in User table.']}
                }, status=400)

            if faculty_exists:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email already exists',
                    'errors': {'email': ['This email address is already registered in Faculty table.']}
                }, status=400)
            
            # Create user
            temp_password = str(uuid.uuid4())
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=temp_password,
                    first_name=first_name,
                    last_name=last_name
                )
                logger.info(f"Successfully created user with ID: {user.id}")
            except IntegrityError as e:
                logger.error(f"IntegrityError while creating user: {str(e)}")
                # Double check if the user was created despite the error
                if User.objects.filter(username=username).exists():
                    logger.error("User exists after IntegrityError!")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Database error while creating user',
                    'errors': {'database': ['Could not create user due to a database constraint.', str(e)]}
                }, status=400)
            except Exception as e:
                logger.error(f"Unexpected error while creating user: {str(e)}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error creating user',
                    'errors': {'database': [str(e)]}
                }, status=400)

            # Set user as active
            user.is_active = True
            user.save()

            # Parse hire date
            try:
                hire_date = timezone.make_aware(
                    datetime.strptime(request.POST['hire_date'], '%Y-%m-%d')
                )
            except ValueError:
                hire_date = timezone.now()

            # Double check again before creating faculty
            if Faculty.objects.filter(email=email).exists():
                logger.error(f"Faculty with email {email} exists before creation!")
                user.delete()
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email already exists',
                    'errors': {'email': ['This email address is already registered in Faculty table (detected during creation).']}
                }, status=400)

            # Create the faculty profile
            try:
                # Try to clean up any potential orphaned records first
                try:
                    Faculty.objects.filter(email=email).delete()
                except Exception as e:
                    logger.error(f"Error cleaning up potential orphaned faculty records: {str(e)}")

                faculty = Faculty.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    job_role=request.POST['job_role'],
                    engineering_dept=request.POST.get('department', ''),
                    email=email,
                    phone=request.POST['phone'].replace('(', '').replace(')', '').replace(' ', '').replace('-', ''),
                    office_room=request.POST['office_room'],
                    hire_date=hire_date
                )
                logger.info(f"Successfully created faculty with ID: {faculty.faculty_id}")
            except IntegrityError as e:
                # If faculty creation fails, delete the user to maintain consistency
                logger.error(f"IntegrityError while creating faculty profile: {str(e)}")
                # Double check if the faculty was created despite the error
                if Faculty.objects.filter(email=email).exists():
                    logger.error("Faculty exists after IntegrityError!")
                user.delete()
                return JsonResponse({
                    'status': 'error',
                    'message': 'Database error while creating faculty profile',
                    'errors': {'database': ['Could not create faculty profile. The email might already be in use.', str(e)]}
                }, status=400)
            except Exception as e:
                # If faculty creation fails for any other reason, delete the user
                logger.error(f"Unexpected error while creating faculty profile: {str(e)}")
                user.delete()
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error creating faculty profile',
                    'errors': {'database': [str(e)]}
                }, status=400)

            # Create default tasks for the new faculty
            try:
                from tasks.models import Task
                default_tasks = Task.objects.all()
                for task in default_tasks:
                    task.assigned_to.add(faculty)
                logger.info(f"Successfully added default tasks for faculty {faculty.faculty_id}")
            except Exception as e:
                logger.error(f"Error adding default tasks for faculty {faculty.faculty_id}: {str(e)}")
                # Don't fail the whole operation if adding tasks fails

            return JsonResponse({
                'status': 'success',
                'user_id': user.id,
                'message': f'Successfully added {faculty.first_name} {faculty.last_name}.'
            })
            
        except Exception as e:
            logger.error(f"Error adding faculty: {str(e)}")
            # If we caught an exception here, make sure to clean up any created user
            try:
                if 'user' in locals():
                    user.delete()
            except Exception:
                pass
            return JsonResponse({
                'status': 'error',
                'message': 'Error adding faculty',
                'details': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

@login_required
@user_passes_test(is_admin)
def import_faculty_csv(request):
    """Handle importing faculty members from CSV"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        try:
            import csv
            from io import TextIOWrapper
            
            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
            reader = csv.DictReader(csv_file)
            
            success_count = 0
            error_messages = []
            
            for row in reader:
                try:
                    # Create user
                    email = f"{row['email']}@sandiego.edu"
                    username = row['username']
                    temp_password = str(uuid.uuid4())
                    
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=temp_password,
                        first_name=row['first_name'],
                        last_name=row['last_name']
                    )

                    # Parse hire date
                    try:
                        hire_date = timezone.make_aware(datetime.strptime(row['hire_date'], '%Y-%m-%d %H:%M'))
                    except ValueError:
                        hire_date = timezone.now()
                    
                    # Create faculty profile
                    faculty = Faculty.objects.create(
                        user=user,
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        job_role=row['job_role'],
                        engineering_dept=row['engineering_dept'],
                        email=email,
                        phone=row['phone'].replace('(', '').replace(')', '').replace(' ', '').replace('-', ''),
                        zoom_phone=row.get('zoom_phone', '').replace('(', '').replace(')', '').replace(' ', '').replace('-', ''),
                        office_room=row['office_room'],
                        hire_date=hire_date,
                        mailing_list_status=row.get('mailing_list_status', '').lower() == 'true',
                        bio=row.get('bio', ''),
                        completed_onboarding=row.get('completed_onboarding', '').lower() == 'true',
                        last_welcome_shown=timezone.now() if row.get('completed_onboarding', '').lower() == 'true' else None
                    )
                    
                    # Add default tasks
                    from tasks.models import Task
                    default_tasks = Task.objects.all()
                    for task in default_tasks:
                        task.assigned_to.add(faculty)
                    
                    success_count += 1
                    messages.success(request, f'Added {faculty.first_name} {faculty.last_name}. Temporary password: {temp_password}')
                except Exception as e:
                    error_messages.append(f"Error adding {row.get('email', 'unknown')}: {str(e)}")
            
            if error_messages:
                messages.warning(request, f'Imported {success_count} faculty members with {len(error_messages)} errors.')
                for error in error_messages:
                    messages.error(request, error)
            else:
                messages.success(request, f'Successfully imported {success_count} faculty members.')
            
            return JsonResponse({'status': 'success', 'imported': success_count})
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def assign_role(request):
    """
    Assign role and permissions to a faculty member
    """
    try:
        user_id = request.POST.get('user_id')
        user_type = request.POST.get('user_type')
        permissions = request.POST.getlist('permissions[]')
        
        faculty = get_object_or_404(Faculty, user_id=user_id)
        
        # Update user type
        if user_type == 'admin':
            faculty.is_admin = True
            # Add user to admin group
            admin_group, _ = Group.objects.get_or_create(name='Admin')
            faculty.user.groups.add(admin_group)
            
            # Set permissions if provided
            if permissions:
                for perm in permissions:
                    # Here you would set the specific permissions
                    # This depends on your permission model
                    pass
        else:
            faculty.is_admin = False
            # Remove user from admin group
            admin_group = Group.objects.filter(name='Admin').first()
            if admin_group:
                faculty.user.groups.remove(admin_group)
        
        faculty.save()
        faculty.user.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Role assigned successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
