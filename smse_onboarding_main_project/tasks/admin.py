"""
Admin file.
"""
from django.contrib import admin

from .models import Task, Faculty

# Register models.
#admin.site.register(Task)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'deadline')
    search_fields = ('title', 'deadline')

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    search_fields = ('first_name', 'email')
    list_filter = ('first_name',)

    def assigned_tasks(self, obj):
        return ", ".join([task.title for task in obj.tasks.all()])
    assigned_tasks.short_description = "Assigned Tasks"

    list_display += ('assigned_tasks',)
