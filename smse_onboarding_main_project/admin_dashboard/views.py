from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from tasks.models import Task, Faculty, TaskProgress
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.models import User

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

    faculty_tasks = [
        {
            'id': 1,
            'name': 'Harley Quinn',
            'current_task': 'Request computer',
            'completion_percentage': 50,
            'status_class': 'approaching',
            'remaining_days': -94,
            'all_tasks': []
        },
        {
            'id': 2,
            'name': 'Bruce Wayne',
            'current_task': 'Request office key',
            'completion_percentage': 60,
            'status_class': 'upcoming',
            'remaining_days': -90,
            'all_tasks': []
        },
        {
            'id': 3,
            'name': 'Clark Kent',
            'current_task': 'Request mailbox',
            'completion_percentage': 20,
            'status_class': 'overdue',
            'remaining_days': -90,
            'all_tasks': []
        },
        {
            'id': 4,
            'name': 'Diana Prince',
            'current_task': 'Complete Security Training',
            'completion_percentage': 100,
            'status_class': 'completed',
            'remaining_days': -71,
            'all_tasks': []
        }
    ]

    admin_tasks = [
        {
            'title': 'Send Welcome Gift',
            'assigned_to': 'Clark Kent',
            'deadline': timezone.now() + timezone.timedelta(days=30),
            'completed': False
        },
        {
            'title': 'Assign Office',
            'assigned_to': 'Clark Kent',
            'deadline': timezone.now() + timezone.timedelta(days=45),
            'completed': False
        },
        {
            'title': 'Task 3',
            'assigned_to': 'Bruce Wayne',
            'deadline': timezone.now() + timezone.timedelta(days=60),
            'completed': True
        }
    ]

    context = {
        'faculty_tasks': faculty_tasks,
        'admin_tasks': admin_tasks,
    }
    
    return render(request, 'admin_dashboard/admin_dashboard.html', context) 