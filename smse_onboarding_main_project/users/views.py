from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate
from .models import Faculty
from django.utils import timezone
from django.contrib.auth.models import User
import logging

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
                        email=user.email,
                        hire_date=timezone.now(),
                        job_role="New Faculty",
                        engineering_dept="SMSE",
                        phone="0000000000",
                        office_room="TBD",
                        last_welcome_shown=timezone.now()
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
