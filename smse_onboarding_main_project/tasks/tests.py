from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse

from tasks.models import Task
from tasks.models import Faculty
from tasks.models import Admin


class TaskTests(TestCase):
    """
    Unit tests for the Task model and related view logic using mocks.

    Args:
        TestCase: Inherits from the TestCase class.
    """

    @patch('tasks.models.Task.objects.create')  # Mock the create method
    def test_task_creation(self, mock_create):
        """
        Test the creation of a Task object using a mock.

        Args:
            mock_create: Create the mock.
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

    @patch('tasks.models.Task.objects.create')
    def test_task_creation_invalid_data(self, mock_create):
        """
        Test that creates a task with invalid data raises an error.

        Args:
            mock_create: Create the mock.
        """
        mock_create.side_effect = ValueError("Invalid data")

        with self.assertRaises(ValueError):
            Task.objects.create(
                title=None,  # Invalid: title is required
                description="This is a test task.",
                deadline=None,  # Invalid: deadline is required
                completed=False,
            )

        mock_create.assert_called_once()

    @patch('tasks.models.Task.objects.all')  # Mock the all method
    def test_task_ordering(self, mock_all):
        """
        Test that tasks are ordered by `created_at` field.

        Args:
            mock_all: Mock all of the mock tasks.
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

    @patch('tasks.models.Task.objects.create')
    def test_task_creation_with_past_deadline(self, mock_create):
        """
        Test that a task with a past deadline raises a validation error.

        Args:
            mock_create: Create the mock.
        """
        past_deadline = datetime(2020, 1, 1, tzinfo=timezone.utc)

        mock_create.side_effect = ValueError("Deadline cannot be in the past")

        with self.assertRaises(ValueError):
            Task.objects.create(
                title="Invalid Task",
                description="Task with past deadline",
                deadline=past_deadline,
                completed=False,
            )

        mock_create.assert_called_once()

    @patch('tasks.views.get_object_or_404')  # Mock the get_object_or_404 method
    def test_complete_task_success(self, mock_get_object_or_404):
        """
        Test marking a task as completed using mocked database functions.

        Args:
            mock_get_object_or_404: Mock the get_object_or_404 function.
        """
        # Set up the mocked task
        mock_task = Mock()
        mock_task.completed = False
        mock_task.save = Mock()
        mock_get_object_or_404.return_value = mock_task

        # Simulate completing the task
        response = self.client.post(reverse('tasks:complete_task', args=[1]))

        mock_get_object_or_404.assert_called_once_with(Task, id=1)
        mock_task.save.assert_called_once()
        self.assertTrue(mock_task.completed)  # Explicitly check the field
        self.assertEqual(response.status_code, 302)

    @patch('tasks.models.Task.save')  # Mock the save method
    def test_complete_task_mock_save(self, mock_save):
        """
        Test that the save method is called when marking a task as complete.

        Args:
            mock_save: Save a mock task.
        """
        # Set up a mocked task
        mock_task = Mock()
        mock_task.save = mock_save

        # Simulate saving a task
        mock_task.save()

        mock_save.assert_called_once()

    @patch('tasks.views.get_object_or_404')
    def test_complete_task_response(self, mock_get_object_or_404):
        """
        Test that the response for completing a task is as expected.

        Args:
            mock_get_object_or_404: Mock the get_object_or_404 function.
        """
        # Set up the mocked task
        mock_task = Mock()
        mock_task.completed = False
        mock_task.save = Mock()
        mock_get_object_or_404.return_value = mock_task

        # Simulate completing the task
        response = self.client.post(reverse('tasks:complete_task', args=[1]))

        self.assertEqual(response.status_code, 302)  # Check redirect

    def test_task_update_status(self):
        """
        Test updating the completed status of a task.
        """
        # Mock a task instance
        mock_task = Mock()
        mock_task.completed = False

        # Simulate status update
        mock_task.completed = True
        self.assertTrue(mock_task.completed)

class LoginTests(TestCase):
    
    @patch('tasks.models.Faculty.objects.create')  # Mock the create method
    def test_faculty_creation(self, mock_create):
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
            faculty_id = 1,
            first_name = "Test",
            last_name = "Faculty",
            job_role = "Professor",
            engineering_dept = "Computer Science",
            password = "password",
            email = "testfaculty@sandiego.edu",
            phone = "8581234567",
            zoom_phone = "6192601234",
            office_room = "GH101",
            hire_date = datetime(2025, 1, 9, 2, 57, 1, tzinfo=timezone.utc),
            mailing_list_status = False,
            bio = "This is a test bio",
        )

        mock_create.assert_called_once_with(
            faculty_id = 1,
            first_name = "Test",
            last_name = "Faculty",
            job_role = "Professor",
            engineering_dept = "Computer Science",
            password = "password",
            email = "testfaculty@sandiego.edu",
            phone = "8581234567",
            zoom_phone = "6192601234",
            office_room = "GH101",
            hire_date = datetime(2025, 1, 9, 2, 57, 1, tzinfo=timezone.utc),
            mailing_list_status = False,
            bio = "This is a test bio",
        )

        self.assertEqual(mock_faculty, faculty)

    @patch('tasks.models.Admin.objects.create')  # Mock the create method
    def test_admin_creation(self, mock_create):
        mock_admin = Mock()
        mock_admin.faculty_id = 1
        mock_admin.first_name = "Test"
        mock_admin.last_name = "Admin"
        mock_admin.job_role = "Admin"
        mock_admin.engineering_dept = "Computer Science"
        mock_admin.password = "password"
        mock_admin.email = "testadmin@sandiego.edu"
        mock_admin.phone = "8581234567"
        mock_admin.zoom_phone = "6192601234"
        mock_admin.office_room = "GH101"
        mock_admin.hire_date = datetime(2025, 1, 9, 2, 57, 1, tzinfo=timezone.utc)
        mock_admin.mailing_list_status = False
        mock_admin.bio = "This is a test bio"
        mock_admin.permissions = "These are test permissions"
        mock_create.return_value = mock_admin

        admin = Admin.objects.create(
            faculty_id = 1,
            first_name = "Test",
            last_name = "Admin",
            job_role = "Admin",
            engineering_dept = "Computer Science",
            password = "password",
            email = "testadmin@sandiego.edu",
            phone = "8581234567",
            zoom_phone = "6192601234",
            office_room = "GH101",
            hire_date = datetime(2025, 1, 9, 2, 57, 1, tzinfo=timezone.utc),
            mailing_list_status = False,
            bio = "This is a test bio",
            permissions = "These are test permissions",
        )

        mock_create.assert_called_once_with(
            faculty_id = 1,
            first_name = "Test",
            last_name = "Admin",
            job_role = "Admin",
            engineering_dept = "Computer Science",
            password = "password",
            email = "testadmin@sandiego.edu",
            phone = "8581234567",
            zoom_phone = "6192601234",
            office_room = "GH101",
            hire_date = datetime(2025, 1, 9, 2, 57, 1, tzinfo=timezone.utc),
            mailing_list_status = False,
            bio = "This is a test bio",
            permissions = "These are test permissions",
        )

        self.assertEqual(mock_admin, admin)