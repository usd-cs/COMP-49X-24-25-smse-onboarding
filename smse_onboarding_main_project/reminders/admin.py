from django.contrib import admin
from .models import Reminder

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    """
    This class customizes the Django Admin panel for managing reminders.
    """
    list_display = ('faculty', 'task', 'reminder_date', 'is_read')
    search_fields = ('faculty__first_name', 'faculty__last_name', 'task__title')
    list_filter = ('is_read', 'faculty', 'task', 'reminder_date')
