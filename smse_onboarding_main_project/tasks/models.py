from django.db import models

# Create your models here.

from django.contrib.auth.models import User

class Task(models.Model):
    title = models.TextField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    deadline = models.DateTimeField()

    class Meta:
        ordering = ['created_at']
