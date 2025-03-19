from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from tasks.models import Faculty
from .models import FacultyDocument
import os
from django.conf import settings

class DocumentTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        #faculty member
        self.faculty = Faculty.objects.create(
            user=self.user,
            first_name='Test',
            last_name='Faculty',
            job_role='Professor',
            engineering_dept='Computer Science',
            email='test@example.com',
            phone='1234567890',
            office_room='123',
            hire_date='2024-01-01 00:00:00'
        )

        # test document
        self.test_file = SimpleUploadedFile(
            "test_doc.txt",
            b"This is a test document.",
            content_type="text/plain"
        )

        self.document = FacultyDocument.objects.create(
            faculty=self.faculty,
            title="Test Document",
            file=self.test_file,
            uploaded_by=self.user
        )

        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def tearDown(self):
        """Clean up test files"""
        # Delete test files from storage
        if self.document.file:
            if os.path.isfile(self.document.file.path):
                os.remove(self.document.file.path)

    def test_show_documents_view(self):
        """Test the document list view"""
        response = self.client.get(reverse('documents:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/document_list.html')
        self.assertIn('documents', response.context)
        self.assertEqual(len(response.context['documents']), 1)

    def test_upload_document(self):
        """Test document upload functionality"""
        test_file = SimpleUploadedFile(
            "new_doc.txt",
            b"This is a new test document.",
            content_type="text/plain"
        )

        response = self.client.post(reverse('documents:upload'), {
            'title': 'New Test Document',
            'document': test_file
        })

        self.assertEqual(response.status_code, 302)  # Redirect after successful upload
        self.assertTrue(FacultyDocument.objects.filter(title='New Test Document').exists())

    def test_download_document(self):
        """Test document download functionality"""
        response = self.client.get(
            reverse('documents:download', args=[self.document.document_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')

    def test_delete_document(self):
        """Test document deletion"""
        response = self.client.post(
            reverse('documents:delete', args=[self.document.document_id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        self.assertFalse(
            FacultyDocument.objects.filter(document_id=self.document.document_id).exists()
        )

    def test_unauthorized_access(self):
        """Test unauthorized access to documents"""
        # Create another user and faculty
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        other_faculty = Faculty.objects.create(
            user=other_user,
            first_name='Other',
            last_name='Faculty',
            job_role='Professor',
            engineering_dept='Computer Science',
            email='other@example.com',
            phone='0987654321',
            office_room='456',
            hire_date='2024-01-01 00:00:00'
        )

        # Login as other user
        self.client.login(username='otheruser', password='otherpass123')

        # Try to download document
        response = self.client.get(
            reverse('documents:download', args=[self.document.document_id])
        )
        self.assertEqual(response.status_code, 403)  # Should be forbidden
