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

    class Meta:
        """Orders the task by creation date"""
        ordering = ['created_at']

from django.db import models

# Non-Admin Faculty Table


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

# Admin Table


class Admin(Faculty):
    """
    Model for admin.

    Args:
        models.Model: Inherits from the Faculty class.
    """
    
    permissions = models.CharField(max_length=255)

# Task Progress Table


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
        return f"Document {self.document_id} for Faculty {self.faculty_id}"

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