from django.contrib.auth.models import User
from django.db import models
from django.db.models import Manager, QuerySet
from django.utils import timezone
from typing import Optional, Any
from users.models import Faculty

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
    prerequisite_task: Optional['Task'] = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL
    )  # Allow tasks to depend on another task

    #assigned_to = models.ManyToManyField('Faculty', related_name='tasks', blank=True)  # blank lets it exist without needing an assignment
    assigned_to = models.ManyToManyField(Faculty, related_name='tasks', blank=True)

    objects: Manager[Any] = Manager()

    def __str__(self):
        return f"{self.title}"

    class Meta:
        ordering = ['created_at']

    def is_unlocked(self) -> bool:
        """Check if the task is available: prerequisite task must be completed."""
        if not self.prerequisite_task:
            return True
        # Get the actual Task instance
        prereq = Task.objects.get(id=self.prerequisite_task.id)
        return bool(prereq.completed)

    def is_completed_by(self, faculty):
        """
        Check if a task is completed by a specific faculty by checking if a TaskProgress record exists.
        """
        from .models import TaskProgress
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

    objects: Manager[Any] = models.Manager()

    class DoesNotExist(Exception):
        pass



