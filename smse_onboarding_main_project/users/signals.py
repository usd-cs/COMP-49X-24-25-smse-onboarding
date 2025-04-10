from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Faculty
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_faculty_profile(sender, instance, created, **kwargs):
    """Create a faculty profile when a new user is created"""
    if created:
        faculty = Faculty.objects.create(
            user=instance,
            first_name=instance.first_name or instance.email.split('@')[0],
            last_name=instance.last_name or '',
            email=instance.email,
            hire_date=timezone.now(),
            job_role="New Faculty",
            engineering_dept="SMSE",
            phone="0000000000",
            office_room="TBD",
            last_welcome_shown=timezone.now()  # Set the last_welcome_shown field
        )
        # Create some default tasks for the new faculty
        from tasks.models import Task
        default_tasks = Task.objects.all()
        for task in default_tasks:
            task.assigned_to.add(faculty)

@receiver(user_logged_in)
def set_welcome_banner(sender, user, request, **kwargs):
    """Set welcome banner when user logs in"""
    # Only set welcome banner if it's not already set
    if 'show_welcome_banner' not in request.session:
        request.session['show_welcome_banner'] = True
        logger.debug(f"Setting welcome banner for user {user.email}")
