"""
Admin file.
"""
from django.contrib import admin
from django.contrib.auth.models import User
from .models import Task, Faculty, TaskProgress, FacultyDocument

# Register models.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Customizes the Django Admin panel for managing tasks.
    It shows task details, allows filtering and searching, and
    shows tasks assignments. 

    """
    list_display = ('title', 'assigned_to', 'completed', 'deadline')
    search_fields = ('title', 'assigned_to__first_name', 'assigned_to__last_name')
    list_filter = ('completed',)

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):

    """
    This class customizes the Django Admin panel for managing faculty members.
    It categorizes faculty based on their onboarding status and user role and
    allows search and filtering.
    """
    list_display = ('first_name', 'last_name', 'engineering_dept', 'email', 'completed_onboarding', 'user_type')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('engineering_dept', 'completed_onboarding')

    def user_type(self, obj):
        """
        Determines the role of a faculty member based on user permissions and onboarding status.

        Args:
            obj (Faculty): The faculty.

        Returns:
            str: Represents the user's role.
        """

        if obj.user.is_superuser:
            return "Superuser Admin"
        elif obj.user.is_staff:
            return "SMSE Admin"
        elif not obj.completed_onboarding:
            return "New Hire"
        else:
            return "Faculty"

    user_type.short_description = "User Role"

@admin.register(FacultyDocument)
class FacultyDocumentAdmin(admin.ModelAdmin):
    """
    This class customizes the Django Admin panel for managing faculty documents.
    It allows searching and displaying faculty document information.
    """
    list_display = ('faculty', 'file_path')
    search_fields = ('faculty__first_name', 'faculty__last_name')
