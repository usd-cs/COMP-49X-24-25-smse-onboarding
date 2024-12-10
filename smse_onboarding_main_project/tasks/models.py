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
