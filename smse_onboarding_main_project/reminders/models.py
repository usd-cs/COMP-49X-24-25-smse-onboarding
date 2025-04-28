from django.db import models
from django.contrib.auth.models import User
from users.models import Faculty
from tasks.models import Task
from django.utils import timezone
from django.db.models import Manager

class Reminder(models.Model):
    """
    Model for a reminder for a faculty user.
    """
    reminder_id = models.AutoField(primary_key=True)
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    reminder_date = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    message = models.TextField()

    objects: Manager = Manager()

    def __str__(self):
        return f"Reminder for {self.faculty.first_name} - {self.task.title}"

    def is_marked_as_read(self):
        return self.is_read
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
    
    class Meta:
        ordering = ['-reminder_date']
    
    class DoesNotExist(Exception):
        pass
