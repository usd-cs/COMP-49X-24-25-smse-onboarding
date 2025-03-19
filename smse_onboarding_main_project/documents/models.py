from django.db import models
from users.models import Faculty
from django.contrib.auth.models import User
from django.db.models import Manager
from django.utils import timezone
import os
from typing import Optional, Any

class FacultyDocument(models.Model):
    """
    Model for a document uploaded by a faculty user.
    """
    document_id = models.AutoField(primary_key=True)
    faculty: Faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='faculty_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by: Optional[User] = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    objects: Manager = Manager()

    def __str__(self) -> str:
        """Return string representation of document."""
        # Use faculty_id instead of id
        faculty_instance = Faculty.objects.get(faculty_id=self.faculty.faculty_id)
        return f"{self.title} - {faculty_instance.first_name}'s Document"

    def delete(self, *args, **kwargs):
        # Delete the file from storage
        if self.file:
            storage = self.file.storage
            name = self.file.name
            if storage.exists(name):
                storage.delete(name)
        super().delete(*args, **kwargs)
