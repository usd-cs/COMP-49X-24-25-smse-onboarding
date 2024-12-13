"""
Admin file.
"""
from django.contrib import admin

from .models import Task

# Register models.
admin.site.register(Task)
