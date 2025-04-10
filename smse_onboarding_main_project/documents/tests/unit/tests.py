from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from unittest.mock import patch, Mock, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.conf import settings
from users.models import Faculty
from documents.models import FacultyDocument
import os
import json
from django.contrib.messages.storage.fallback import FallbackStorage


class DocumentTests(TestCase):
    """Unit tests for document management functionality with mocked models."""

    def setUp(self):
        """
        Set up test environment with mocked objects.
        
        Creates:
        - Factory for requests
        - Mock user
        - Mock faculty
        - Mock document
        - Test file
        - Mock client
        """
        # Create request factory for more controlled testing
        self.factory = RequestFactory()

        # Create mock user with authentication status
        self.mock_user = MagicMock()
        self.mock_user.username = 'testuser'
        self.mock_user.is_authenticated = True
        self.mock_user.is_staff = False

        # Create mock faculty
        self.mock_faculty = MagicMock(spec=Faculty)
        self.mock_faculty.faculty_id = 1
        self.mock_faculty.user = self.mock_user
        self.mock_faculty.first_name = 'Test'
        self.mock_faculty.last_name = 'Faculty'

        # Add faculty_profile to mock user
        self.mock_user.faculty_profile = self.mock_faculty

        # Create test file
        self.test_file = SimpleUploadedFile(
            "test_doc.txt",
            b"This is a test document.",
            content_type="text/plain"
        )

        # Create mock document
        self.mock_document = MagicMock(spec=FacultyDocument)
        self.mock_document.document_id = 1
        self.mock_document.faculty = self.mock_faculty
        self.mock_document.title = "Test Document"
        self.mock_document.file = MagicMock()
        self.mock_document.file.url = '/media/test_doc.txt'
        self.mock_document.file.name = 'faculty_documents/test_doc.txt'
        self.mock_document.uploaded_by = self.mock_user
        self.mock_document.uploaded_at = '2023-01-01T00:00:00Z'

        # Set up client
        self.client = Client()

    def add_session_to_request(self, request):
        """Helper method to add session to a request object"""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        # Add messages storage to request
        setattr(request, '_messages', FallbackStorage(request))

        # Add user to request
        request.user = self.mock_user

        return request

    def tearDown(self):
        """Clean up test files."""
        if hasattr(self, 'test_file') and self.test_file:
            if os.path.exists(self.test_file.name):
                os.remove(self.test_file.name)

    @patch('documents.views.render')
    @patch('documents.views.get_object_or_404')
    @patch('documents.models.FacultyDocument.objects.filter')
    def test_show_documents_view(self, mock_filter, mock_get_object, mock_render):
        """Test the document list view with mocked queries."""
        # Create request
        request = self.factory.get(reverse('documents:show_documents'))
        request = self.add_session_to_request(request)

        # Set up mocks
        mock_get_object.return_value = self.mock_faculty
        mock_filter.return_value = [self.mock_document]
        mock_render.return_value = MagicMock(status_code=200)

        # Import here to avoid module-level patching issues
        from documents.views import show_documents

        # Call the view directly
        response = show_documents(request)

        # Verify mocks were called correctly
        mock_get_object.assert_called_once_with(Faculty, user=request.user)
        mock_filter.assert_called_once()
        self.assertEqual(response.status_code, 200)

    @patch('documents.views.get_object_or_404')
    @patch('documents.views.JsonResponse')
    def test_upload_document(self, mock_json_response, mock_get_object):
        """Test document upload functionality with mocked storage."""
        # Setup POST request with file
        url = reverse('documents:upload_document')
        request = self.factory.post(
            url,
            {
                'title': 'New Test Document',
                'faculty': '1'  # Faculty ID
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        request.FILES['document'] = self.test_file
        request = self.add_session_to_request(request)

        # Set up mocks
        mock_get_object.return_value = self.mock_faculty
        mock_json_response.return_value = MagicMock(status_code=200, content=json.dumps({'status': 'success'}).encode())

        # Mock FacultyDocument creation
        document_mock = MagicMock()

        with patch('documents.views.FacultyDocument', return_value=document_mock):
            # Import and call view
            from documents.views import upload_document
            response = upload_document(request)

        # Verify mocks and expectations
        if not request.user.is_staff:
            mock_get_object.assert_called_once_with(Faculty, user=request.user)

        document_mock.save.assert_called_once()
        self.assertEqual(response.status_code, 200)

    @patch('documents.views.get_object_or_404')
    @patch('documents.views.os.path.exists')
    @patch('documents.views.open')
    @patch('documents.views.FileResponse')
    def test_download_document(self, mock_file_response, mock_open, mock_path_exists, mock_get_object):
        """Test document download functionality with mocked file operations."""
        # Create request
        url = reverse('documents:download_document', args=[1])
        request = self.factory.get(url)
        request = self.add_session_to_request(request)

        # Set up mocks
        mock_get_object.return_value = self.mock_document
        mock_path_exists.return_value = True
        mock_file = MagicMock()
        mock_open.return_value = mock_file
        mock_file_response.return_value = MagicMock(status_code=200)

        # Import and call view
        from documents.views import download_document
        response = download_document(request, doc_id=1)

        # Verify mocks and expectations
        mock_get_object.assert_called_once_with(FacultyDocument, document_id=1)
        mock_path_exists.assert_called_once()
        mock_open.assert_called_once()
        self.assertEqual(response.status_code, 200)

    @patch('documents.views.get_object_or_404')
    @patch('documents.views.JsonResponse')
    def test_delete_document(self, mock_json_response, mock_get_object):
        """Test document deletion with mocked storage."""
        # Create request
        url = reverse('documents:delete_document', args=[1])
        request = self.factory.post(
            url,
            {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        request = self.add_session_to_request(request)

        # Set up mocks
        mock_document = MagicMock(spec=FacultyDocument)
        mock_document.faculty = self.mock_faculty
        mock_get_object.return_value = mock_document
        mock_json_response.return_value = MagicMock(status_code=200, content=json.dumps({'status': 'success'}).encode())

        # Import and call view
        from documents.views import delete_document
        response = delete_document(request, doc_id=1)

        # Verify mocks and expectations
        mock_get_object.assert_called_once_with(FacultyDocument, document_id=1)
        mock_document.delete.assert_called_once()
        self.assertEqual(response.status_code, 200)

    @patch('documents.views.get_object_or_404')
    def test_unauthorized_access(self, mock_get_object):
        """Test unauthorized document access."""
        # Create unauthorized mock user
        unauthorized_user = MagicMock()
        unauthorized_user.is_authenticated = True
        unauthorized_user.is_staff = False

        # Create a faculty that's different from the document owner
        other_faculty = MagicMock(spec=Faculty)
        other_faculty.faculty_id = 2
        unauthorized_user.faculty_profile = other_faculty

        # Create request
        url = reverse('documents:download_document', args=[1])
        request = self.factory.get(url)

        # Add session and set unauthorized user
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        request.user = unauthorized_user

        # Set up document mock to belong to a different faculty
        mock_document = MagicMock(spec=FacultyDocument)
        mock_document.faculty = self.mock_faculty  # Faculty with ID 1
        mock_get_object.return_value = mock_document

        # Import and call view
        from documents.views import download_document
        from django.core.exceptions import PermissionDenied

        # Verify PermissionDenied is raised
        with self.assertRaises(PermissionDenied):
            download_document(request, doc_id=1)
