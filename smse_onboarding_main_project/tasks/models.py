from django.contrib.auth.models import User
from django.db import models


class Task(models.Model):
    """
    Model for a task.
    
    Args:
        models.Model: Inherits from the models.Model class.
    """
    title = models.TextField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    deadline = models.DateTimeField()
    assigned_to = models.ForeignKey('Faculty', on_delete=models.CASCADE, related_name='tasks')
    #assigned_to = models.CharField(max_length=255)  # ForeignKey if needed

    def __str__(self):
        return f"{self.title}" # should make the Django admin show the task title instead of "task object (1)"

    class Meta:
        """Orders the task by creation date"""
        ordering = ['created_at']

class Faculty(models.Model):
    """
    Model for non-admin faculty.

    Args:
        models.Model: Inherits from the models.Model class.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="faculty_profile")  # links to jdjango default User
    faculty_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    job_role = models.CharField(max_length=255)
    engineering_dept = models.CharField(max_length=255)
    #password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=10)
    zoom_phone = models.CharField(max_length=10)
    office_room = models.CharField(max_length=20)
    hire_date = models.DateTimeField()
    mailing_list_status = models.BooleanField(default=False)
    bio = models.TextField(blank=True)

    completed_onboarding = models.BooleanField(default=False) #helps flag new hires from reg

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Admin Table


class TaskProgress(models.Model):
    """
    Model for a task's progress.

    Args:
        models.Model: Inherits from the models.Model class.
    """

    progress_id = models.AutoField(primary_key=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    progress_status = models.CharField(max_length=255)

    def __str__(self):
        return f"Task Progress {self.progress_id}"

# Faculty Documents Table


class FacultyDocument(models.Model):
    """
    Model for a document uploaded by a faculty user.

    Args:
        models.Model: Inherits from the models.Model class.
    """

    document_id = models.AutoField(primary_key=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.faculty.first_name}'s Document"
# Other Employees Table



class OtherEmployee(models.Model):
    """
    Model for other employees such as those from ITS and HR.

    Args:
        models.Model: Inherits from the models.Model class.
    """

    other_employee_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    job_role = models.CharField(max_length=255)
    other_employee_dept = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=10)
    office_room = models.CharField(max_length=20)
    associated_tasks = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
