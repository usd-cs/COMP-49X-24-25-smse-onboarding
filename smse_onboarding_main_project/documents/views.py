from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, FileResponse
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import FacultyDocument
from tasks.models import Faculty
import os

# Create your views here.

@login_required
def show_documents(request):
    """Shows documents for the logged-in user"""
    user = request.user

    if user.is_staff:
        documents = FacultyDocument.objects.all().order_by('-uploaded_at')
    else:
        faculty = get_object_or_404(Faculty, user=user)
        documents = FacultyDocument.objects.filter(faculty=faculty)

    template_name = 'tasks/admin_document_list.html' if user.is_staff else 'tasks/document_list.html'

    context = {
        'documents': documents,
        'user': user,
    }

    return render(request, template_name, context)

@login_required
def upload_document(request):
    """View for uploading documents"""
    if request.method == 'POST':
        try:
            # Check if user is staff or has permission for the faculty
            if request.user.is_staff:
                faculty = request.user.faculty_profile
            else:
                faculty = get_object_or_404(Faculty, user=request.user)
                # Add this check to prevent uploading for other faculty
                if 'faculty_id' in request.POST:
                    target_faculty = get_object_or_404(Faculty, id=request.POST['faculty_id'])
                    if faculty != target_faculty:
                        raise PermissionDenied

            document = FacultyDocument(
                faculty=faculty,
                title=request.POST.get('title'),
                file=request.FILES['document'],
                uploaded_by=request.user
            )
            document.save()
            messages.success(request, 'Document uploaded successfully!')

        except PermissionDenied:
            # Return 403 instead of redirecting
            return JsonResponse({'error': 'Permission denied'}, status=403)
        except Exception as e:
            messages.error(request, f'Error uploading document: {str(e)}')

        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect(f"{reverse('tasks:home')}?show_documents=true")

    if request.user.is_staff:
        return redirect('admin_dashboard')
    return redirect('tasks:home')

@login_required
def delete_document(request, doc_id):
    """View for deleting documents"""
    if request.method == 'POST':
        try:
            document = get_object_or_404(FacultyDocument, document_id=doc_id)

            # Check permissions - return 403 if not authorized
            if not request.user.is_staff and (not hasattr(request.user, 'faculty_profile') or
                                            request.user.faculty_profile != document.faculty):
                return JsonResponse({'error': 'Permission denied'}, status=403)

            document.delete()
            messages.success(request, 'Document deleted successfully!')

            if request.user.is_staff:
                return redirect('admin_dashboard')
            return redirect(f"{reverse('tasks:home')}?show_documents=true")

        except Exception as e:
            messages.error(request, f'Error deleting document: {str(e)}')
            return JsonResponse({'error': str(e)}, status=400)

    if request.user.is_staff:
        return redirect('admin_dashboard')
    return redirect(f"{reverse('tasks:home')}?show_documents=true")

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
        return redirect('tasks:home')
