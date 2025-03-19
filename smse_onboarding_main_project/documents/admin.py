from django.contrib import admin
from .models import FacultyDocument

@admin.register(FacultyDocument)
class FacultyDocumentAdmin(admin.ModelAdmin):
    """
    This class customizes the Django Admin panel for managing faculty documents.
    """
    list_display = ('title', 'faculty', 'uploaded_by', 'uploaded_at')
    search_fields = ('title', 'faculty__first_name', 'faculty__last_name')
    list_filter = ('uploaded_at', 'faculty')
