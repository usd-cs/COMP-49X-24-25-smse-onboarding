from django.contrib import admin
from .models import Faculty
from django.utils.safestring import mark_safe

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('faculty_id', 'first_name', 'last_name', 'job_role', 'engineering_dept', 'email')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('engineering_dept', 'job_role', 'completed_onboarding')
    readonly_fields = ['profile_image_preview']

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return mark_safe(f'<img src="{obj.profile_image.url}" width="150" />')
        return "No Image"

    profile_image_preview.short_description = 'Image Preview'
