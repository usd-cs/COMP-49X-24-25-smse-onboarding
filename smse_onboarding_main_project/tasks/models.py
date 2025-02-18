from django.db import models

class Task(models.Model):
    """
    Model for a task.
    """
    title = models.TextField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    deadline = models.DateTimeField()
    prerequisite_task = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL
    )  # Allow tasks to depend on another task

    class Meta:
        ordering = ['created_at']

    def is_unlocked(self):
        """Check if the task is available: prerequisite task must be completed."""
        if self.prerequisite_task:
            return self.prerequisite_task.completed
        return True

    def __str__(self):
        return self.title

class Faculty(models.Model):
    """
    Model for non-admin faculty.
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

class Admin(Faculty):
    """
    Model for admin.
    """
    permissions = models.CharField(max_length=255)

class TaskProgress(models.Model):
    """
    Model for a task's progress.
    """
    progress_id = models.AutoField(primary_key=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    progress_status = models.CharField(max_length=255)

    def __str__(self):
        return f"Task Progress {self.progress_id}"

class FacultyDocument(models.Model):
    """
    Model for a document uploaded by a faculty user.
    """
    document_id = models.AutoField(primary_key=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=255)

    def __str__(self):
        return f"Document {self.document_id} for Faculty {self.faculty.faculty_id}"

class OtherEmployee(models.Model):
    """
    Model for other employees such as those from ITS and HR.
    """
    other_employee_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    job_role = models.CharField(max_length=255)
    other_employee_dept = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=10)
    office_room = models.CharField(max_length=20)
    associated_tasks = models.ManyToManyField(Task, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
