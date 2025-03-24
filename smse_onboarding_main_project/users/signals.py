from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Faculty
from django.utils import timezone

@receiver(post_save, sender=User)
def create_faculty_profile(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        # Create faculty profile for new users
        faculty = Faculty.objects.create(
            user=instance,
            first_name=instance.first_name or instance.email.split('@')[0],
            last_name=instance.last_name or '',
            email=instance.email,
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
