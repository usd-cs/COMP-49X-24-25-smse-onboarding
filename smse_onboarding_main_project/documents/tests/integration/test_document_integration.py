from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Faculty
from documents.models import FacultyDocument
from tasks.models import Task, TaskProgress
from documents.views import show_documents
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.core.management import call_command

class DocumentIntegrationTests(TestCase):
    """Integration tests for document functionality"""
    
    fixtures = ['document_test_data.json']  # Load document-specific test data

    def setUp(self):
        """Set up test data using document_test_data.json fixtures"""
        # Get existing users from fixtures
        self.user1 = User.objects.get(username='longpham')
        self.user2 = User.objects.get(username='sbello')

        # Get existing faculty from fixtures
        self.faculty1 = Faculty.objects.get(user=self.user1)
        self.faculty2 = Faculty.objects.get(user=self.user2)

        # Get existing documents from fixtures
        self.document1 = FacultyDocument.objects.get(faculty=self.faculty1, title='Long Pham - CV')
        self.document2 = FacultyDocument.objects.get(faculty=self.faculty2, title='Shayna Bello - Resume')

        self.client = Client()

    def reset_fixtures(self):
        """Reset the database to the initial fixture state"""
        # Clear all data
        TaskProgress.objects.all().delete()
        Task.objects.all().delete()
        Faculty.objects.all().delete()
        User.objects.all().delete()
        FacultyDocument.objects.all().delete()
        
        # # Reload fixtures
        # call_command('loaddata', 'test_data.json', verbosity=0)
        
    def test_show_document(self):
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

        self.reset_fixtures()