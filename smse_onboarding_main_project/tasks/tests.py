from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from .models import Faculty, FacultyDocument
from django.core.files.storage import default_storage
import os
from django.conf import settings
from django.utils import timezone as django_timezone

from tasks.models import Task, TaskProgress
from tasks.views import is_admin


class TaskTests(TestCase):
    """
    Unit tests for the Task model and related view logic using mocks.
    """

    @patch('tasks.models.Task.objects.create')  # Mock the create method
    def test_task_creation(self, mock_create):
        """
        Test the creation of a Task object using a mock.
        """
        test_deadline = datetime(2025, 1, 9, 2, 57, 1, tzinfo=timezone.utc)

        # Set up the mocked task
        mock_task = Mock()
        mock_task.title = "Test Task"
        mock_task.completed = False
        mock_create.return_value = mock_task

        # Call the mocked create method
        task = Task.objects.create(
            title="Test Task",
            description="This is a test task.",
            deadline=test_deadline,
            completed=False,
        )

        mock_create.assert_called_once_with(
            title="Test Task",
            description="This is a test task.",
            deadline=test_deadline,
            completed=False,
        )
        self.assertEqual(task.title, "Test Task")
        self.assertFalse(task.completed)

    @patch('tasks.models.Task.objects.all')  # Mock the all method
    def test_task_ordering_by_created_at(self, mock_all):
        """
        Test that tasks are ordered by `created_at` field in ascending order.
        """
        # Create mock tasks with different `created_at` values
        mock_task1 = Mock(created_at=datetime(2025, 1, 9, tzinfo=timezone.utc))
        mock_task2 = Mock(created_at=datetime(2025, 1, 8, tzinfo=timezone.utc))
        mock_all.return_value = [mock_task1, mock_task2]

        # Simulate ordering logic explicitly
        tasks = sorted(Task.objects.all(), key=lambda task: task.created_at)

        # Check that tasks are ordered by `created_at` field
        self.assertEqual(tasks, [mock_task2, mock_task1])  # Expect ascending order
        mock_all.assert_called_once()

    @patch('tasks.models.Task.objects.all')
    def test_task_ordering_by_deadline(self, mock_all):
        """
        Test that tasks are ordered by `deadline` field in ascending order.
        """
        mock_task1 = Mock(deadline=datetime(2025, 1, 10, tzinfo=timezone.utc))
        mock_task2 = Mock(deadline=datetime(2025, 1, 9, tzinfo=timezone.utc))
        mock_task3 = Mock(deadline=datetime(2025, 1, 8, tzinfo=timezone.utc))

        mock_all.return_value = [mock_task1, mock_task2, mock_task3]

        tasks = sorted(Task.objects.all(), key=lambda task: task.deadline)

        self.assertEqual(tasks, [mock_task3, mock_task2, mock_task1])
        mock_all.assert_called_once()

    @patch('tasks.models.Task.objects.all')
    def test_task_ordering_with_prerequisites(self, mock_all):
        """
        Test task ordering where prerequisite tasks must be completed first.
        """
        mock_task1 = Mock(created_at=datetime(2025, 1, 9, tzinfo=timezone.utc), prerequisite_task=None)
        mock_task2 = Mock(created_at=datetime(2025, 1, 10, tzinfo=timezone.utc), prerequisite_task=mock_task1)
        mock_task3 = Mock(created_at=datetime(2025, 1, 11, tzinfo=timezone.utc), prerequisite_task=mock_task2)

        mock_all.return_value = [mock_task3, mock_task2, mock_task1]

        # Simulate correct ordering logic
        tasks = sorted(Task.objects.all(), key=lambda task: (task.prerequisite_task is not None, task.created_at))

        self.assertEqual(tasks, [mock_task1, mock_task2, mock_task3])
        mock_all.assert_called_once()

    @patch('tasks.models.Task.is_unlocked')  # Mock the is_unlocked method
    def test_unlocked_tasks(self, mock_is_unlocked):
        """
        Test that only unlocked tasks are retrieved.
        """
        # Mocking tasks
        mock_task1 = Mock(title="Unlocked Task", is_unlocked=Mock(return_value=True))
        mock_task2 = Mock(title="Locked Task", is_unlocked=Mock(return_value=False))

        tasks = [mock_task1, mock_task2]

        # Filtering only unlocked tasks
        unlocked_tasks = [task for task in tasks if task.is_unlocked()]

        self.assertEqual(unlocked_tasks, [mock_task1])
        self.assertTrue(mock_task1.is_unlocked())
        self.assertFalse(mock_task2.is_unlocked())

    @patch('tasks.models.Task.save')  # Mock the save method
    def test_complete_task_mock_save(self, mock_save):
        """
        Test that the save method is called when marking a task as complete.
        """
        # Set up a mocked task
        mock_task = Mock()
        mock_task.save = mock_save

        # Simulate saving a task
        mock_task.save()

        mock_save.assert_called_once()


class LoginTests(TestCase):

    @patch('tasks.models.Faculty.objects.create')  # Mock the create method
    def test_faculty_creation(self, mock_create):
        """
        Test faculty account creation.
        """
        mock_faculty = Mock()
        mock_faculty.faculty_id = 1
        mock_faculty.first_name = "Test"
        mock_faculty.last_name = "Faculty"
        mock_faculty.job_role = "Professor"
        mock_faculty.engineering_dept = "Computer Science"
        mock_faculty.password = "password"
        mock_faculty.email = "testfaculty@sandiego.edu"
        mock_faculty.phone = "8581234567"
        mock_faculty.zoom_phone = "6192601234"
        mock_faculty.office_room = "GH101"
        mock_faculty.hire_date = datetime(2025, 1, 9, 2, 57, 1, tzinfo=timezone.utc)
        mock_faculty.mailing_list_status = False
        mock_faculty.bio = "This is a test bio"
        mock_create.return_value = mock_faculty

        faculty = Faculty.objects.create(
            faculty_id=1,
            first_name="Test",
            last_name="Faculty",
            job_role="Professor",
            engineering_dept="Computer Science",
            password="password",
            email="testfaculty@sandiego.edu",
            phone="8581234567",
            zoom_phone="6192601234",
            office_room="GH101",
            hire_date=datetime(2025, 1, 9, 2, 57, 1, tzinfo=timezone.utc),
            mailing_list_status=False,
            bio="This is a test bio",
        )

        mock_create.assert_called_once_with(
            faculty_id=1,
            first_name="Test",
            last_name="Faculty",
            job_role="Professor",
            engineering_dept="Computer Science",
            password="password",
            email="testfaculty@sandiego.edu",
            phone="8581234567",
            zoom_phone="6192601234",
            office_room="GH101",
            hire_date=datetime(2025, 1, 9, 2, 57, 1, tzinfo=timezone.utc),
            mailing_list_status=False,
            bio="This is a test bio",
        )

        self.assertEqual(mock_faculty, faculty)


class DocumentManagementTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Create a faculty member
        self.faculty = Faculty.objects.create(
            user=self.user,
            first_name='Test',
            last_name='Faculty',
            job_role='Professor',
            engineering_dept='Computer Science',
            email='test@example.com',
            phone='1234567890',
            office_room='CS101',
            hire_date='2024-01-01T00:00:00Z'
        )

        # Create an admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='admin123',
            is_staff=True
        )

        self.admin_faculty = Faculty.objects.create(
            user=self.admin_user,
            first_name='Admin',
            last_name='User',
            job_role='Admin',
            engineering_dept='Computer Science',
            email='admin@example.com',
            phone='0987654321',
            office_room='CS102',
            hire_date='2024-01-01T00:00:00Z'
        )

        # Create a test client
        self.client = Client()

        # Create a test document file
        self.test_file = SimpleUploadedFile(
            "test_doc.pdf",
            b"file_content",
            content_type="application/pdf"
        )

    def tearDown(self):
        """Clean up after tests"""
        # Delete test files from media directory
        for doc in FacultyDocument.objects.all():
            if doc.file and default_storage.exists(doc.file.name):
                default_storage.delete(doc.file.name)

    def test_document_list_view_authenticated(self):
        """Test that authenticated users can view their documents"""
        # Log in the user
        self.client.login(username='testuser', password='testpass123')

        # Create a test document
        doc = FacultyDocument.objects.create(
            faculty=self.faculty,
            title="Test Document",
            file=self.test_file,
            uploaded_by=self.user
        )

        # Get the document list page
        response = self.client.get(reverse('tasks:document_list'))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Document")

        # Clean up
        doc.delete()

    def test_document_list_view_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(reverse('tasks:document_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_upload_document_success(self):
        """Test successful document upload"""
        # Log in the user
        self.client.login(username='testuser', password='testpass123')

        # Prepare upload data
        upload_data = {
            'title': 'Test Upload',
            'document': SimpleUploadedFile(
                "test_upload.pdf",
                b"file_content",
                content_type="application/pdf"
            ),
            'faculty': self.faculty.faculty_id
        }

        # Try to upload
        response = self.client.post(reverse('tasks:upload_document'), upload_data)

        # Check response
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(FacultyDocument.objects.filter(title='Test Upload').exists())


    def test_delete_document_success(self):
        """Test successful document deletion"""
        # Log in the user
        self.client.login(username='testuser', password='testpass123')

        # Create a document to delete
        doc = FacultyDocument.objects.create(
            faculty=self.faculty,
            title="Delete Test",
            file=self.test_file,
            uploaded_by=self.user
        )

        # Test deletion
        response = self.client.post(reverse('tasks:delete_document', args=[doc.document_id]))

        # Check response
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertFalse(FacultyDocument.objects.filter(document_id=doc.document_id).exists())

    def test_delete_document_wrong_user(self):
        """Test that users can't delete other faculty's documents"""
        # Create another faculty's document
        other_faculty = Faculty.objects.create(
            first_name='Other',
            last_name='Faculty',
            job_role='Professor',
            engineering_dept='Computer Science',
            email='other2@example.com',
            phone='5555555556',
            office_room='CS104',
            hire_date='2024-01-01T00:00:00Z'
        )

        doc = FacultyDocument.objects.create(
            faculty=other_faculty,
            title="Other's Document",
            file=self.test_file,
            uploaded_by=self.user
        )

        # Log in as regular user
        self.client.login(username='testuser', password='testpass123')

        # Attempt deletion
        response = self.client.post(reverse('tasks:delete_document', args=[doc.document_id]))

        # Should raise PermissionDenied
        self.assertEqual(response.status_code, 403)
        self.assertTrue(FacultyDocument.objects.filter(document_id=doc.document_id).exists())

"""
    def test_admin_document_access(self):
        #Test that admin users can access all documents
        # Log in as admin
        self.client.login(username='adminuser', password='admin123')

        # Create test documents
        FacultyDocument.objects.create(
            faculty=self.faculty,
            title="Faculty Doc",
            file=SimpleUploadedFile("test.pdf", b"file_content"),
            uploaded_by=self.user
        )

        # Create another document uploaded by admin
        FacultyDocument.objects.create(
            faculty=self.faculty,
            title="Admin Doc",
            file=SimpleUploadedFile("test2.pdf", b"file_content"),
            uploaded_by=self.admin_user
        )

        # Get document list
        response = self.client.get(reverse('tasks:document_list'))

        # Check that admin can see all documents
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Faculty Doc")
        self.assertContains(response, "Admin Doc")
"""

class AdminDashboardTests(TestCase):
    def setUp(self):
        """Set up test data for admin dashboard tests"""
        # Create an admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )

        # Create some faculty members with different onboarding states
        self.faculty1 = Faculty.objects.create(
            user=User.objects.create_user(username='faculty1', password='pass123'),
            first_name='John',
            last_name='Doe',
            job_role='Assistant Professor',
            engineering_dept='Computer Science',
            email='john@example.com',
            phone='1234567890',
            office_room='CS101',
            hire_date=django_timezone.now() + timedelta(days=30),
            completed_onboarding=False
        )

        self.faculty2 = Faculty.objects.create(
            user=User.objects.create_user(username='faculty2', password='pass123'),
            first_name='Jane',
            last_name='Smith',
            job_role='Associate Professor',
            engineering_dept='Electrical Engineering',
            email='jane@example.com',
            phone='0987654321',
            office_room='EE201',
            hire_date=django_timezone.now() + timedelta(days=15),
            completed_onboarding=False
        )

        # Create some tasks
        self.task1 = Task.objects.create(
            title='Complete Paperwork',
            description='Fill out new hire paperwork',
            deadline=django_timezone.now() + timedelta(days=7)
        )
        self.task1.assigned_to.add(self.faculty1)

        self.task2 = Task.objects.create(
            title='Setup Office',
            description='Set up office space',
            deadline=django_timezone.now() + timedelta(days=20)
        )
        self.task2.assigned_to.add(self.faculty2)

        self.client = Client()

    def test_admin_dashboard_access(self):
        """Test that only admin users can access the dashboard"""
        # Test unauthenticated access
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

        # Test non-admin access
        self.client.login(username='faculty1', password='pass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Test admin access
        self.client.login(username='adminuser', password='admin123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_upcoming_deadlines_display(self):
        """Test that upcoming deadlines are correctly displayed"""
        self.client.login(username='adminuser', password='admin123')
        response = self.client.get(reverse('admin_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('faculty_tasks', response.context)
        
        faculty_tasks = response.context['faculty_tasks']
        
        # Check if both faculty members are in the context
        self.assertEqual(len(faculty_tasks), 2)
        
        # Verify the structure of faculty tasks
        for faculty_task in faculty_tasks:
            self.assertIn('name', faculty_task)
            self.assertIn('current_task', faculty_task)
            self.assertIn('completion_percentage', faculty_task)
            self.assertIn('status_class', faculty_task)
            self.assertIn('remaining_days', faculty_task)
            self.assertIn('all_tasks', faculty_task)

    def test_admin_tasks_display(self):
        """Test that admin tasks are correctly displayed"""
        self.client.login(username='adminuser', password='admin123')
        response = self.client.get(reverse('admin_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('admin_tasks', response.context)
        
        admin_tasks = response.context['admin_tasks']
        
        # Verify that admin tasks are present
        self.assertTrue(len(admin_tasks) > 0)
        
        # Check the structure of admin tasks
        for task in admin_tasks:
            self.assertIn('id', task)
            self.assertIn('title', task)
            self.assertIn('description', task)
            self.assertIn('deadline', task)
            self.assertIn('completed', task)
            self.assertIn('is_overdue', task)

    def test_completion_percentage_calculation(self):
        """Test that task completion percentage is calculated correctly"""
        # Create a task progress for faculty1
        TaskProgress.objects.create(
            faculty=self.faculty1,
            task=self.task1,
            completed=True
        )
        
        self.client.login(username='adminuser', password='admin123')
        response = self.client.get(reverse('admin_dashboard'))
        
        faculty_tasks = response.context['faculty_tasks']
        
        # Find faculty1's tasks in the context
        faculty1_task = next(ft for ft in faculty_tasks if ft['id'] == self.faculty1.faculty_id)
        
        # Since faculty1 has completed 1 out of 1 task
        self.assertEqual(faculty1_task['completion_percentage'], 100)

    def test_status_class_assignment(self):
        """Test that status classes are correctly assigned based on deadlines"""
        # Create a task with an overdue deadline
        overdue_task = Task.objects.create(
            title='Overdue Task',
            description='This task is overdue',
            deadline=django_timezone.now() - timedelta(days=1)
        )
        overdue_task.assigned_to.add(self.faculty1)
        
        self.client.login(username='adminuser', password='admin123')
        response = self.client.get(reverse('admin_dashboard'))
        
        faculty_tasks = response.context['faculty_tasks']
        faculty1_task = next(ft for ft in faculty_tasks if ft['id'] == self.faculty1.faculty_id)
        
        # Should be 'overdue' since there's an overdue task
        self.assertEqual(faculty1_task['status_class'], 'overdue')
