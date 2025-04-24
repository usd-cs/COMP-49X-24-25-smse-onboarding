from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from tasks.models import Task, TaskProgress
from users.models import Faculty
from documents.models import FacultyDocument
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from datetime import datetime
import logging
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods

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
@require_http_methods(["POST"])
def create_faculty(request):
    # Add detailed request logging
    logger.info("=== Create Faculty Request ===")
    logger.info(f"Request method: {request.method}")
    logger.info(f"User: {request.user.username}")
    logger.info("POST data:")
    for key, value in request.POST.items():
        if key != 'password' and key != 'password_confirmation':  # Don't log passwords
            logger.info(f"  {key}: {value}")
    logger.info("========================")

    try:
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        
        # Validate required fields
        required_fields = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'engineering_dept': request.POST.get('engineering_dept'),
            'job_role': request.POST.get('job_role'),
            'phone': request.POST.get('phone'),
            'office_room': request.POST.get('office_room'),
            'hire_date': request.POST.get('hire_date'),
            'hire_time': request.POST.get('hire_time')
        }
        
        # Check for missing required fields
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            logger.error(f"Missing required fields: {', '.join(missing_fields)}")
            return JsonResponse({
                'success': False,
                'message': f'Please fill in all required fields: {", ".join(missing_fields)}'
            }, status=400)
        
        # Debug logging for all form data
        logger.debug(f"Received form data for faculty creation:")
        logger.debug(f"Username: {username}")
        logger.debug(f"Email: {email}")
        logger.debug(f"Name: {first_name} {last_name}")
        logger.debug(f"Department: {request.POST.get('engineering_dept')}")
        logger.debug(f"Job Role: {request.POST.get('job_role')}")
        logger.debug(f"Phone: {request.POST.get('phone')}")
        logger.debug(f"Office: {request.POST.get('office_room')}")
        logger.debug(f"Hire Date: {request.POST.get('hire_date')} {request.POST.get('hire_time')}")
        
        # Check if user is admin
        if not is_admin(request.user):
            logger.error(f"Non-admin user {request.user.username} attempted to create faculty")
            return JsonResponse({
                'success': False,
                'message': 'You do not have permission to create faculty members.'
            }, status=403)
        
        # Check if username already exists
        existing_user_by_username = User.objects.filter(username=username).first()
        if existing_user_by_username:
            logger.debug(f"Username {username} already exists for user ID: {existing_user_by_username.id}")
            return JsonResponse({
                'success': False,
                'message': f'Username "{username}" is already taken. Please choose a different username.'
            }, status=400)

        # Check if email already exists in User or Faculty
        existing_user_by_email = User.objects.filter(email=email).first()
        if existing_user_by_email:
            logger.debug(f"Email {email} already exists for user ID: {existing_user_by_email.id}")
            return JsonResponse({
                'success': False,
                'message': f'Email "{email}" is already registered. Please use a different email address.'
            }, status=400)
            
        existing_faculty_by_email = Faculty.objects.filter(email=email).first()
        if existing_faculty_by_email:
            # If there's an existing faculty but no user, delete the faculty record
            if not existing_faculty_by_email.user:
                logger.debug(f"Found orphaned faculty record with ID {existing_faculty_by_email.faculty_id}, deleting it")
                existing_faculty_by_email.delete()
            else:
                logger.debug(f"Email {email} already exists for faculty ID: {existing_faculty_by_email.faculty_id}")
                return JsonResponse({
                    'success': False,
                    'message': f'Email "{email}" is already registered. Please use a different email address.'
                }, status=400)

        # Prepare hire date
        hire_date = request.POST.get('hire_date')
        hire_time = request.POST.get('hire_time', '00:00')  # Default to midnight if not provided
        try:
            hire_datetime = datetime.strptime(f"{hire_date} {hire_time}", '%Y-%m-%d %H:%M')
            logger.debug(f"Parsed hire date: {hire_datetime}")
        except ValueError as e:
            logger.error(f"Invalid date format: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Invalid date format. Please check the date and time.'
            }, status=400)

        # Create User account first
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            logger.debug(f"Created user account with ID: {user.id}")
        except Exception as e:
            logger.error(f"Failed to create user account: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Failed to create user account: {str(e)}'
            }, status=400)

        try:
            # Create Faculty profile with required fields
            faculty = Faculty.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                engineering_dept=request.POST.get('engineering_dept'),
                job_role=request.POST.get('job_role'),
                office_room=request.POST.get('office_room'),
                phone=request.POST.get('phone'),
                email=email,  # Use the same email as the user
                hire_date=hire_datetime
            )
            logger.debug(f"Created faculty profile with ID: {faculty.faculty_id}")

            # Update optional fields if provided
            if zoom_phone := request.POST.get('zoom_phone'):
                faculty.zoom_phone = zoom_phone
                logger.debug(f"Added zoom phone: {zoom_phone}")
            
            if bio := request.POST.get('bio'):
                faculty.bio = bio
                logger.debug(f"Added bio")

            faculty.mailing_list_status = request.POST.get('mailing_list_status') == 'on'
            faculty.completed_onboarding = request.POST.get('completed_onboarding') == 'on'
            
            faculty.save()
            logger.debug(f"Successfully saved faculty with ID: {faculty.faculty_id}")
            
            return JsonResponse({
                'success': True,
                'message': f'Faculty member {first_name} {last_name} created successfully!'
            })
            
        except Exception as e:
            logger.error(f"Error creating faculty profile: {str(e)}")
            # If faculty creation fails, delete the user
            user.delete()
            return JsonResponse({
                'success': False,
                'message': f'Failed to create faculty profile: {str(e)}'
            }, status=400)

    except Exception as e:
        # Clean up any created user if it exists
        if 'user' in locals():
            user.delete()
        
        error_message = str(e)
        logger.error(f"Error in create_faculty: {error_message}")
        
        if 'duplicate key value violates unique constraint' in error_message:
            error_message = 'This email address is already registered in the system. Please use a different email address.'
        
        return JsonResponse({
            'success': False,
            'message': error_message
        }, status=400)
