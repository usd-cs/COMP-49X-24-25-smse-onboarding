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
    prerequisite_task = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL
    )   # Allow tasks to depend on another task

    class Meta:
        """Orders the task by creation date"""
        ordering = ['created_at']

    def is_unlocked(self):
        """Cehck if the tasks is available , prerequisite taks is completed or not"""
        if self.prerequisite_task:
            return self.prerequisite_task.completed
        return True  # No prerequisite task

    def __str__(self):
        return self.title
