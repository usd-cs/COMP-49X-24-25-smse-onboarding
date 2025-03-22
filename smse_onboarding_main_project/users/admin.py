from django.contrib import admin
from .models import Faculty

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('faculty_id', 'first_name', 'last_name', 'job_role', 'engineering_dept', 'email')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('engineering_dept', 'job_role', 'completed_onboarding')
