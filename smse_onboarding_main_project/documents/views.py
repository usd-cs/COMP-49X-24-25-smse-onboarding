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
            # For admin users, show all documents sorted by most recent
            documents = FacultyDocument.objects.all().order_by('-uploaded_at')
            faculties = Faculty.objects.all()
            
            context = {
                'documents': documents,
                'faculties': faculties,
            }
            return render(request, 'documents/list.html', context)
        else:
            # For regular users, show only their documents
            faculty = get_object_or_404(Faculty, user=user)
            documents = FacultyDocument.objects.filter(faculty=faculty)
            context = {
                'documents': documents,
                'faculty': faculty
            }
            return render(request, 'documents/list.html', context)

    # This part only handles the faculty_id case
    return render(request, 'documents/list.html', {
        'documents': documents,
        'faculty': faculty if faculty_id else None,
        'faculties': Faculty.objects.all() if user.is_staff else None
    })

@login_required
def upload_document(request):
    """View for uploading documents"""
    if request.method == 'POST':
        try:
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
            
            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            
            # For regular form submissions, redirect without messages
            return redirect('documents:show_documents')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            return redirect('documents:show_documents')

    # For GET request, show the document list with upload form
    context = {}
    
    if request.user.is_staff:
        context['faculties'] = Faculty.objects.all()
        context['documents'] = FacultyDocument.objects.all().order_by('-uploaded_at')
    else:
        faculty = get_object_or_404(Faculty, user=request.user)
        context['documents'] = FacultyDocument.objects.filter(faculty=faculty)

    return render(request, 'documents/list.html', context)

@login_required
def delete_document(request, doc_id):
    """View for deleting documents"""
    if request.method == 'POST':
        try:
            document = get_object_or_404(FacultyDocument, document_id=doc_id)

            # Check permissions
            if not request.user.is_staff and (not hasattr(request.user, 'faculty_profile') or
                                         request.user.faculty_profile != document.faculty):
                raise PermissionDenied

            document.delete()
            
            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            
            # For regular form submissions, redirect without messages
            return redirect('documents:show_documents')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            return redirect('documents:show_documents')

    return redirect('documents:show_documents')

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
