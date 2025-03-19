from django.db import models
from django.contrib.auth.models import User
from django.db.models import Manager
from typing import Optional, Any


class Faculty(models.Model):
    """
    Model for non-admin faculty.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="faculty_profile", null=True, blank=True)
    faculty_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    job_role = models.CharField(max_length=255)
    engineering_dept = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=10)
    zoom_phone = models.CharField(max_length=10, blank=True, null=True)
    office_room = models.CharField(max_length=20)
    hire_date = models.DateTimeField()
    mailing_list_status = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    completed_onboarding = models.BooleanField(default=False)  # helps flag new hires from reg

    objects: Manager[Any] = models.Manager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

