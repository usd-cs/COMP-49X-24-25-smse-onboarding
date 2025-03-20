from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from tasks.models import Task, TaskProgress
from users.models import Faculty
from documents.models import FacultyDocument

@login_required
def new_hire_home(request):
    """
    Render the new hire dashboard home page
    """
    # TODO move  from tasks/views.py
    # Update template paths to use dashboard/new_hire/
    pass

@login_required
def admin_home(request):
    """
    Render the admin dashboard home page
    """
    # TODO: move from tasks/views.py
    # Update template paths to use dashboard/admi
    pass
