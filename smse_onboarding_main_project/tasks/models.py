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
    #assigned_to = models.ForeignKey('Faculty', on_delete=models.CASCADE, related_name='tasks')
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

    faculty_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    job_role = models.CharField(max_length=255)
    engineering_dept = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=10)
    zoom_phone = models.CharField(max_length=10)
    office_room = models.CharField(max_length=20)
    hire_date = models.DateTimeField()
    mailing_list_status = models.BooleanField(default=False)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
