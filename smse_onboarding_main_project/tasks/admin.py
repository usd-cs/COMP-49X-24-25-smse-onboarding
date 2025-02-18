"""
Admin file.
"""
from django.contrib import admin

from .models import Task

# Register models.
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "completed", "deadline", "prerequisite_task")
    list_filter = ("completed",)
    search_fields = ("title",)
