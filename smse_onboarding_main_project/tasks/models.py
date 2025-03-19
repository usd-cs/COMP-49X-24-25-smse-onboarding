from django.contrib.auth.models import User
from django.db import models
from django.db.models import Manager
from django.utils import timezone

class Task(models.Model):
    """
    Model for a task.
    """
    title = models.TextField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    deadline = models.DateTimeField()
    is_completed_by_faculty = models.BooleanField(default=False)
    prerequisite_task = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL
    )  # Allow tasks to depend on another task

    assigned_to = models.ManyToManyField('Faculty', related_name='tasks', blank=True)  # blank lets it exist without needing an assignment

    objects: Manager = Manager()

    def __str__(self):
        return f"{self.title}"

    class Meta:
        ordering = ['created_at']

    def is_unlocked(self):
        """Check if the task is available: prerequisite task must be completed."""
        if not self.prerequisite_task:
            return True
        return self.prerequisite_task.completed

    def is_completed_by(self, faculty):
        """
        Check if a task is completed by a specific faculty by checking if a TaskProgress record exists.
        """
        return TaskProgress.objects.filter(
            faculty=faculty,
            task=self,
            completed=True
        ).exists()

    def complete_for_faculty(self, faculty):
        """
        Mark a task as completed for a specific faculty by creating a TaskProgress record.
        """
        # Update or create with completed=True
        TaskProgress.objects.update_or_create(
            faculty=faculty,
            task=self,
            defaults={'completed': True}
        )

    def uncomplete_for_faculty(self, faculty):
        """
        Mark a task as not completed for a specific faculty by removing the TaskProgress record.
        We could set completed=False, but deletion is cleaner.
        """
        TaskProgress.objects.filter(faculty=faculty, task=self).delete()

    @property
    def remaining_days(self):
        """Calculate days remaining until deadline"""
        now = timezone.now()
        delta = self.deadline - now
        return delta.days


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

    objects: Manager = Manager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TaskProgress(models.Model):
    """
    Model for a task's progress.
    """
    progress_id = models.AutoField(primary_key=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    completed = models.BooleanField(default=True)

    class Meta:
        # Ensure we only have one progress record per faculty-task pair
        unique_together = ('faculty', 'task')

    def __str__(self):
        return f"{self.faculty} - {self.task} - Completed: {self.completed}"



