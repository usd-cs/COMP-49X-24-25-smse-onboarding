from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, JsonResponse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.conf import settings
from .models import FacultyDocument
from users.models import Faculty
import os

@login_required
def show_documents(request, faculty_id=None):
    """Shows the list of all faculty documents"""
    user = request.user

    if faculty_id:
        faculty = get_object_or_404(Faculty, faculty_id=faculty_id)
        if not user.is_staff and (not hasattr(user, 'faculty_profile') or user.faculty_profile.faculty_id != faculty_id):
            raise PermissionDenied
        documents = FacultyDocument.objects.filter(faculty=faculty)
    else:
        if user.is_staff:
            documents = FacultyDocument.objects.all()
        else:
            faculty = get_object_or_404(Faculty, user=user)
            documents = FacultyDocument.objects.filter(faculty=faculty)

    # Check if this is an AJAX request for modal content
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'documents/modal_content.html', {
            'documents': documents,
            'faculty': faculty if faculty_id else None
        })

    return render(request, 'documents/list.html', {
        'documents': documents,
        'faculty': faculty if faculty_id else None
    })

@login_required
def upload_document(request):
    """View for uploading documents"""
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty')

        if not request.user.is_staff:
            faculty = get_object_or_404(Faculty, user=request.user)
            if str(faculty.faculty_id) != faculty_id:
                raise PermissionDenied

        document = FacultyDocument(
            faculty_id=faculty_id,
            title=request.POST.get('title'),
            file=request.FILES['document'],
            uploaded_by=request.user
        )
        document.save()
        messages.success(request, 'Document uploaded successfully!')
        return JsonResponse({'status': 'success'})

    # For GET request, show the document list with modal
    faculties = Faculty.objects.all() if request.user.is_staff else None
    documents = FacultyDocument.objects.filter(faculty=request.user.faculty_profile) if not request.user.is_staff else FacultyDocument.objects.all()

    return render(request, 'documents/list.html', {
        'documents': documents,
        'faculties': faculties
    })

@login_required
def delete_document(request, doc_id):
    """View for deleting documents"""
    if request.method == 'POST':
        document = get_object_or_404(FacultyDocument, document_id=doc_id)

        # Check permissions
        if not request.user.is_staff and (not hasattr(request.user, 'faculty_profile') or
                                         request.user.faculty_profile != document.faculty):
            raise PermissionDenied

        document.delete()
        messages.success(request, 'Document deleted successfully!')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def download_document(request, doc_id):
    """View for downloading documents"""
    document = get_object_or_404(FacultyDocument, document_id=doc_id)

    # Check permissions
    if not request.user.is_staff and (not hasattr(request.user, 'faculty_profile') or
                                     request.user.faculty_profile != document.faculty):
        raise PermissionDenied

    file_path = os.path.join(settings.MEDIA_ROOT, document.file.name)
    if os.path.exists(file_path):
        # Get file extension and actual MIME type
        file_ext = os.path.splitext(document.file.name)[1].lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        content_type = content_types.get(file_ext, 'application/octet-stream')

        # Use the actual filename from storage
        filename = os.path.basename(document.file.name)

        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        messages.error(request, 'File not found.')
        return JsonResponse({'status': 'error', 'message': 'File not found'}, status=404)
