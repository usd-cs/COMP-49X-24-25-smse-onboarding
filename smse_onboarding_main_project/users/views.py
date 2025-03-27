from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate
from .models import Faculty
from django.utils import timezone
from django.contrib.auth.models import User

# Create your views here.

def login(request):
    """Handle user login"""
    if request.method == 'POST':
        # Get username and password from POST data
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # Redirect based on user type
            if user.is_superuser:
                return redirect('admin_dashboard')
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
                        office_room="TBD"
                    )
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
