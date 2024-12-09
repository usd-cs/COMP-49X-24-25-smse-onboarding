from django.db import models

# Non-Admin Faculty Table


class Faculty(models.Model):
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
    permissions = models.CharField(max_length=255)

# Task Table


class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=255)
    due_date = models.DateTimeField()
    created_date = models.DateTimeField(auto_now_add=True)
    completed_status = models.BooleanField(default=False)
    assigned_to = models.CharField(max_length=255)  # ForeignKey if needed
    description = models.TextField(blank=True)

    def __str__(self):
        return self.task_name

# Task Progress Table


class TaskProgress(models.Model):
    progress_id = models.AutoField(primary_key=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    progress_status = models.CharField(max_length=255)

    def __str__(self):
        return f"Task Progress {self.progress_id}"

# Faculty Documents Table


class FacultyDocument(models.Model):
    document_id = models.AutoField(primary_key=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=255)

    def __str__(self):
        return f"Document {self.document_id} for Faculty {self.faculty_id}"

# Other Employees Table


class OtherEmployee(models.Model):
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
