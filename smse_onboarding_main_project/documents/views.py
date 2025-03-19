from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, FileResponse
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import FacultyDocument
from users.models import Faculty
import os
import mimetypes

# Create your views here.

@login_required
def show_documents(request):
    """Display list of documents for the current faculty."""
    try:
        faculty = Faculty.objects.get(user=request.user)
        documents = FacultyDocument.objects.filter(faculty=faculty)
        return render(request, 'documents/list.html', {
            'documents': documents,
            'faculty': faculty
        })
    except Faculty.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return redirect('tasks:home')

@login_required
def upload_document(request):
    """Handle document upload."""
    if request.method == 'POST':
        try:
            faculty = Faculty.objects.get(user=request.user)
            title = request.POST.get('title')
            document = request.FILES.get('document')

            if title and document:
                FacultyDocument.objects.create(
                    faculty=faculty,
                    title=title,
                    file=document,
                    uploaded_by=request.user
                )
                messages.success(request, 'Document uploaded successfully.')
            else:
                messages.error(request, 'Please provide both title and document.')
        except Faculty.DoesNotExist:
            messages.error(request, 'Faculty profile not found.')

    return redirect('documents:list')

@login_required
def delete_document(request, doc_id):
    """Handle document deletion."""
    if request.method == 'POST':
        document = get_object_or_404(FacultyDocument, document_id=doc_id)

        # Check if user has permission to delete
        if document.faculty.user != request.user and not request.user.is_staff:
            raise PermissionDenied

        document.delete()
        messages.success(request, 'Document deleted successfully.')

    return redirect('documents:list')

@login_required
def download_document(request, doc_id):
    """Handle document download."""
    document = get_object_or_404(FacultyDocument, document_id=doc_id)

    # Check if user has permission to download
    if document.faculty.user != request.user and not request.user.is_staff:
        raise PermissionDenied

    file_path = document.file.path
    if os.path.exists(file_path):
        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or 'application/octet-stream'

        filename = os.path.basename(document.file.name)
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    messages.error(request, 'File not found.')
    return redirect('documents:list')
