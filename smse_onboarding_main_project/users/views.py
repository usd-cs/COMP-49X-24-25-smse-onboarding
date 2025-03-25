from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login as auth_login
from .models import Faculty
from django.utils import timezone
from django.contrib.auth.models import User

# Create your views here.

def login(request):
    """Handle user login"""
    if request.user.is_authenticated:
        # Check if user is superuser
        if request.user.is_superuser:
            return redirect('admin_dashboard')

        # Try to get or create faculty profile
        try:
            faculty = Faculty.objects.get(user=request.user)
        except Faculty.DoesNotExist:
            # Create new faculty profile from Google data
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
            # Create some default tasks for the new faculty
            from tasks.models import Task
            default_tasks = Task.objects.all()
            for task in default_tasks:
                task.assigned_to.add(faculty)

            messages.info(request, 'Welcome! Please complete your profile.')

        return redirect('tasks:home')

    return render(request, 'users/auth/login.html')

@login_required
def profile(request):
    """Display user profile"""
    try:
        faculty = Faculty.objects.get(user=request.user)
        return render(request, 'users/profile/details.html', {'faculty': faculty})
    except Faculty.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return redirect('users:login')
