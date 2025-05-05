from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate
from .models import Faculty
from django.utils import timezone
from django.contrib.auth.models import User
import logging
from django.http import HttpResponse

logger = logging.getLogger(__name__)

# Create your views here.

def login(request):
    """Handle user login"""
    # If already authenticated, direct to appropriate dashboard
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        elif request.user.is_staff:
            return redirect('dashboard:admin_home')
        else:
            return redirect('dashboard:new_hire_home')

    if request.method == 'POST':
        # Get username and password from POST data
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            logger.debug(f"User {user.email} successfully logged in")

            # Set welcome banner only on when user logs in
            request.session['show_welcome_banner'] = True
            logger.debug(f"Setting show_welcome_banner=True for user {user.email}")

            # Redirect based on user type
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif user.is_staff:
                return redirect('dashboard:admin_home')
            else:
                try:
                    faculty = Faculty.objects.get(user=user)
                except Faculty.DoesNotExist:
                    faculty = Faculty.objects.create(
                        user=user,
                        first_name=user.first_name or user.email.split('@')[0],
                        last_name=user.last_name or '',
                        date_of_birth="1990-01-01T00:00:00-08:00",
                        email=user.email,
                        hire_date=timezone.now(),
                        job_role="New Faculty",
                        engineering_dept="SMSE",
                        phone="0000000000",
                        office_room="TBD"
                    )
                    from tasks.models import Task
                    default_tasks = Task.objects.all()
                    for task in default_tasks:
                        task.assigned_to.add(faculty)

                    messages.info(request, 'Welcome! Please complete your profile.')

                return redirect('dashboard:new_hire_home')

        # If login failed
        messages.error(request, 'Invalid username or password.')
        return redirect('users:login')

    return render(request, 'users/auth/login.html')

@login_required
def profile(request):
    """Display user profile"""
    try:
        faculty = Faculty.objects.get(user=request.user)
        return render(request, 'users/profile/details.html', {'faculty': faculty})
    except Faculty.DoesNotExist:
        # Create a new faculty profile if one doesn't exist
        faculty = Faculty.objects.create(
            user=request.user,
            first_name=request.user.first_name or request.user.email.split('@')[0],
            last_name=request.user.last_name or '',
            date_of_birth="1990-01-01T00:00:00-08:00",
            email=request.user.email,
            hire_date=timezone.now(),
            job_role="New Faculty",
            engineering_dept="SMSE",
            phone="0000000000",
            office_room="TBD"
        )
        return render(request, 'users/profile/details.html', {'faculty': faculty})

@login_required
def dismiss_welcome_banner(request):
    """Dismiss the welcome banner for this session"""
    request.session['show_welcome_banner'] = False
    logger.debug(f"User {request.user.email} dismissed welcome banner")
    # Get the referer URL to redirect back to the same page
    referer = request.META.get('HTTP_REFERER', None)
    if referer:
        return redirect(referer)
    elif request.user.is_staff:
        return redirect('dashboard:admin_home')
    else:
        return redirect('dashboard:new_hire_home')

@login_required
def show_welcome(request):
    """Show the welcome banner"""
    # Set session variable to show the banner
    request.session['show_welcome_banner'] = True
    logger.debug(f"User {request.user.email} requested to show welcome banner")

    # Get the referer URL to redirect back to the same page
    referer = request.META.get('HTTP_REFERER', None)
    if referer:
        return redirect(referer)
    elif request.user.is_staff:
        return redirect('dashboard:admin_home')
    else:
        return redirect('dashboard:new_hire_home')

@login_required
def welcome_info(request):
    """Display detailed welcome information page"""
    return render(request, 'users/newhire_help_guide.html')

@login_required
def admin_help_guide(request):
    """Display the admin help guide page"""
    return render(request, 'users/admin_help_guide.html')

@login_required
def test_profile_image(request):
    """Test view to check if profile image is working"""
    try:
        faculty = Faculty.objects.get(user=request.user)
        context = {
            'faculty': faculty,
            'has_image': bool(faculty.profile_image),
            'image_url': faculty.profile_image.url if faculty.profile_image else None,
            'image_path': faculty.profile_image.path if faculty.profile_image else None,
        }
        return render(request, 'users/profile/test_image.html', context)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

@login_required
def update_profile(request):
    """Update user profile information"""
    if request.method == 'POST':
        try:
            # Get the faculty object
            faculty = Faculty.objects.get(user=request.user)

            # Update username if provided
            if 'username' in request.POST and request.POST['username'].strip():
                request.user.username = request.POST['username'].strip()
                request.user.save()

            # Update job role if provided
            if 'job_role' in request.POST and request.POST['job_role'].strip():
                faculty.job_role = request.POST['job_role'].strip()

            # Update date of birth if provided
            if 'date_of_birth' in request.POST and request.POST['date_of_birth'].strip():
                faculty.date_of_birth = request.POST['date_of_birth'].strip()

            # Update office if provided
            if 'office' in request.POST and request.POST['office'].strip():
                faculty.office_room = request.POST['office'].strip()

            # Update bio if provided
            if 'bio' in request.POST and request.POST['bio'].strip():
                faculty.bio = request.POST['bio'].strip()

            # Update profile picture if provided
            if 'profile_picture' in request.FILES:
                try:
                    # Add debug logging
                    logger.debug(f"Uploading profile image for user {request.user.username}")
                    faculty.profile_image = request.FILES['profile_picture']
                    logger.debug(f"Image assigned to faculty: {faculty.profile_image}")
                    faculty.save()
                    logger.debug(f"Faculty saved with image: {faculty.profile_image.url}")
                except Exception as e:
                    logger.error(f"Error saving profile image: {str(e)}")
                    messages.error(request, f"Error saving profile image: {str(e)}")
            else:
                # Save faculty changes if no image was uploaded
                faculty.save()

            messages.success(request, 'Profile updated successfully!')

        except Faculty.DoesNotExist:
            messages.error(request, 'Faculty profile not found.')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')

    # Redirect back to referring page
    referer = request.META.get('HTTP_REFERER', None)
    if referer:
        return redirect(referer)
    else:
        return redirect('dashboard:new_hire_home')
