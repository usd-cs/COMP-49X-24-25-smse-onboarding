from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Faculty
from documents.models import FacultyDocument
from documents.views import show_documents, upload_document
from django.utils import timezone
from datetime import datetime
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile

class DocumentIntegrationTests(TestCase):
    """Integration tests for document functionality"""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests in this class."""
        
        User.objects.all().delete()
        # Create users
        cls.user1 = User.objects.create_user(
            pk=1,
            username='longpham',
            password='password123',
            email='longpham@sandiego.edu',
            is_active=True
        )
        cls.user2 = User.objects.create_user(
            pk=2,
            username='sbello',
            password='password123',
            email='sbello@sandiego.edu',
            is_active=True
        )

        Faculty.objects.all().delete()
        # Create faculty
        cls.faculty1 = Faculty.objects.create(
            user=cls.user1,
            faculty_id=1,
            first_name='Long',
            last_name='Pham',
            job_role='Professor',
            engineering_dept='Computer Science',
            email='longpham@sandiego.edu',
            phone='1234567890',
            zoom_phone='0987654321',
            office_room='CS101',
            hire_date='2024-01-15T08:00:00-08:00',
            mailing_list_status=False,
            bio='Test bio',
            completed_onboarding=False
        )
        cls.faculty2 = Faculty.objects.create(
            user=cls.user2,
            faculty_id=2,
            first_name='Shayna',
            last_name='Bello',
            job_role='Assistant Professor',
            engineering_dept='Electrical Engineering',
            email='sbello@sandiego.edu',
            phone='987654321',
            zoom_phone='0123456789',
            office_room='EE102',
            hire_date='2024-02-01T08:00:00-08:00',
            mailing_list_status=True,
            bio='Another test bio',
            completed_onboarding=False
        )

        FacultyDocument.objects.all().delete()
        # Create documents
        cls.document1 = FacultyDocument.objects.create(
            faculty=cls.faculty1,
            title='Long Pham - CV',
            file='faculty_documents/longpham_cv.pdf',
            uploaded_by=cls.user1,
        )
        cls.document1.uploaded_at = datetime(2024, 1, 15, 8, 0, 0, tzinfo=timezone.get_default_timezone())
        cls.document1.save(update_fields=['uploaded_at'])
        cls.document2 = FacultyDocument.objects.create(
            faculty=cls.faculty2,
            title='Shayna Bello - Resume',
            file='faculty_documents/sbello_resume.pdf',
            uploaded_by=cls.user2,
        )
        cls.document2.uploaded_at = datetime(2024, 2, 1, 8, 0, 0, tzinfo=timezone.get_default_timezone())
        cls.document2.save(update_fields=['uploaded_at'])

    def setUp(self):
        """Set up for each test."""
        self.client = Client()
        
    def test_show_document_flow(self):
        """Test that a document can be shown successfully"""
        self.client.login(username='longpham', password='password123')
        request = self.client.get(reverse('documents:faculty_documents', args=[self.faculty1.faculty_id]), follow=True).wsgi_request
        request.user = self.user1 # Set the user on the request

        # Call the view function directly
        response = show_documents(request, self.faculty1.faculty_id)
        
        # Check the final response after following redirects
        self.assertEqual(response.status_code, 200)

        # Since we can't access context directly, let's check the content
        self.assertIn(str(self.document1.title).encode(), response.content)
        self.assertNotIn(str(self.document2.title).encode(), response.content)

    def test_permission_denied(self):
        """Test that a user cannot view a document that they do not have access to"""
        self.client.login(username='sbello', password='password123')
        request = self.client.get(reverse('documents:faculty_documents', args=[self.faculty1.faculty_id])).wsgi_request
        request.user = self.user2  # Set the user on the request

        # Test that PermissionDenied is raised
        with self.assertRaises(PermissionDenied):
            show_documents(request, self.faculty1.faculty_id)

    def test_upload_document_flow(self):
        """Test that a document can be uploaded successfully"""
        self.client.login(username='longpham', password='password123')
        
        # Create a test file with more content to ensure it's not empty
        test_file = SimpleUploadedFile(
            'test.pdf',
            content=b'This is a test PDF file content',
            content_type='application/pdf'
        )
        
        # Use the client's post method with proper data and files
        response = self.client.post(
            reverse('documents:upload_document'),
            {
                'faculty': str(self.faculty1.faculty_id),
                'title': 'Test Document',
            },
            files={'document': test_file}
        )

        self.assertEqual(response.status_code, 302)
        
        # Get the request from the response
        request = response.wsgi_request
        request.user = self.user1
        
        # Call the view function directly with the prepared request
        response2 = upload_document(request)
        
        self.assertEqual(response2.status_code, 302)

    def test_delete_document_flow(self):
        """Test that a document can be deleted successfully"""
        self.client.login(username='longpham', password='password123')

        test_document = FacultyDocument.objects.create(
            faculty=self.faculty1,
            title='test document',
            file='faculty_documents/longpham_cv.pdf',
            uploaded_by=self.user1,
            uploaded_at='2024-01-15T08:00:00-08:00'
        )

        self.assertEqual(FacultyDocument.objects.count(), 3)

        response = self.client.post(
            reverse('documents:delete_document', args=[test_document.document_id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(FacultyDocument.objects.count(), 2)
        self.assertIsNone(FacultyDocument.objects.filter(document_id=test_document.document_id).first())

    def test_order_of_documents(self):
        """Test that documents are ordered by uploaded_at"""
        self.client.login(username='longpham', password='password123')

        # Create an admin user for this test
        admin_user = User.objects.create_user(
            pk=3,
            username='admin',
            password='password123',
            email='admin@sandiego.edu',
            is_active=True,
            is_staff=True
        )

        request = self.client.get(reverse('documents:faculty_documents', args=[self.faculty1.faculty_id]), follow=True).wsgi_request
        request.user = admin_user # Set the user on the request

        # Call the view function directly
        response = show_documents(request, None)
        
        # Check the final response after following redirects
        self.assertEqual(response.status_code, 200)
        
        # Get the response content as a string
        content = response.content.decode('utf-8')
        
        # Find the positions of the titles in the content
        title1_pos = content.find(self.document1.title)
        title2_pos = content.find(self.document2.title)
        
        # Verify that document2 (more recent) appears before document1 (older)
        self.assertGreater(title1_pos, title2_pos, 
                         f"Expected {self.document2.title} to appear before {self.document1.title}")