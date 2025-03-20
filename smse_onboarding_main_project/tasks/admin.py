"""
Admin file.
"""
from django.contrib import admin
from .models import Task, TaskProgress

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Customizes the Django Admin panel for managing tasks.
    It shows task details, allows filtering and searching, and
    shows tasks assignments. 

    """
    list_display = ('title', 'deadline', 'completed')
    list_filter = ('completed', 'deadline')
    search_fields = ('title', 'description')

@admin.register(TaskProgress)
class TaskProgressAdmin(admin.ModelAdmin):
    """
    This class customizes the Django Admin panel for managing task progress.
    It allows searching and displaying task progress information.
    """
    list_display = ('faculty', 'task', 'completed')
    list_filter = ('completed',)
    search_fields = ('faculty__first_name', 'faculty__last_name', 'task__title')
