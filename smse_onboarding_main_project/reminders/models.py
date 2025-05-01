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
    secondary_faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='secondary_reminders',
        null=True,
        blank=True
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    reminder_date = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    title = models.TextField(default="")
    message = models.TextField(default="")

    objects: Manager = Manager()

    def __str__(self):
        return f"Reminder for {self.faculty.first_name} - {self.task.title}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
    
    def mark_as_unread(self):
        self.is_read = False
        self.save()
    
    class Meta:
        ordering = ['-reminder_date']
    
    class DoesNotExist(Exception):
        pass
