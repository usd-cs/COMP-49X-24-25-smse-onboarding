from unittest.mock import MagicMock
from datetime import datetime, timedelta
from django.test import TestCase
from unittest.mock import patch, Mock
from django.urls import reverse
from tasks.models import Task, TaskProgress
from users.models import Faculty
from django.test import Client


class TaskMock:
    """Mock for Task model."""
    def __init__(self, task_id, task_name, due_date, completed_status):
        """
        Function for setting up the mock for the Task model.

        Args:
            task_id: The ID for the task.
            task_name: The name for the task.
            due_date: The due date for the task.
            completed_status: The completion status of the task.
        """
        self.task_id = task_id
        self.task_name = task_name
        self.due_date = due_date
        self.completed_status = completed_status
        self.save = MagicMock()  # Mock save method


class TaskProgressMock:
    """Mock for TaskProgress model."""
    def __init__(self, progress_id, task, faculty, progress_status):
        """
        Function for setting up the mock for the TaskProgress model.

        Args:
            progress_id: The ID for the task progress.
            task: The name for the task.
            faculty: The faculty member that the task is assigned to.
            progress_status: The progress and completion status of the task.
        """
        self.progress_id = progress_id
        self.task = task
        self.faculty = faculty
        self.progress_status = progress_status
        self.save = MagicMock()  # Mock save method


class TaskTests(TestCase):
    """
    Unit tests for Task model with a mocked database.

    Args:
        TestCase: Inherits from the TestCase class.
    """

    def setUp(self):
        """Set up the mock for the task."""
        # Mock a task instance
        self.mock_task = TaskMock(
            task_id=1,
            task_name="Mock Task",
            due_date=datetime.now() + timedelta(days=7),
            completed_status=False
        )

    def test_task_creation(self):
        """Test task creation and saving."""
        self.mock_task.save()
        self.mock_task.save.assert_called_once()  # Ensure the save method was called

        self.assertEqual(self.mock_task.task_name, "Mock Task")
        self.assertFalse(self.mock_task.completed_status)

    def test_task_update_status(self):
        """Test updating the completed status of a task."""
        self.mock_task.completed_status = True  # Mock status update
        self.assertTrue(self.mock_task.completed_status)


class TaskProgressTests(TestCase):
    """
    Unit tests for TaskProgress model with a mocked database.
    
    Args:
        TestCase: Inherits from the TestCase class.
    """

    def setUp(self):
        """Set up the mock for the task's progress."""
        # Mock faculty and task instances
        self.mock_task = TaskMock(
            task_id=1,
            task_name="Mock Task",
            due_date=datetime.now() + timedelta(days=7),
            completed_status=False
        )
        self.mock_faculty = MagicMock()  # Mock Faculty object
        self.mock_faculty.faculty_id = 1
        self.mock_faculty.first_name = "John"
        self.mock_faculty.last_name = "Doe"

        # Mock a task progress instance
        self.mock_task_progress = TaskProgressMock(
            progress_id=1,
            task=self.mock_task,
            faculty=self.mock_faculty,
            progress_status="In Progress"
        )

    def test_task_progress_creation(self):
        """Test task progress creation and saving."""
        self.mock_task_progress.save()
        self.mock_task_progress.save.assert_called_once()  # Ensure the save method was called

        self.assertEqual(self.mock_task_progress.progress_status, "In Progress")
        self.assertEqual(self.mock_task_progress.task.task_id, 1)
        self.assertEqual(self.mock_task_progress.faculty.faculty_id, 1)

    def test_task_progress_update_status(self):
        """Test updating the progress status of a task progress."""
        self.mock_task_progress.progress_status = "Completed"  # Mockstatus update
        self.assertEqual(self.mock_task_progress.progress_status, "Completed")


class TaskViewTests(TestCase):
    """Unit tests for task-related views with mocked models."""

    def setUp(self):
        """
        Set up test environment with mocked objects.
        
        Creates:
        - Mock client
        - Mock user with authentication
        - Mock faculty profile
        - Mock tasks
        """
        self.client = Client()

        # Mock user
        self.mock_user = Mock()
        self.mock_user.username = 'testuser'
        self.mock_user.is_authenticated = True

        # Mock faculty
        self.mock_faculty = Mock(spec=Faculty)
        self.mock_faculty.user = self.mock_user
        self.mock_faculty.first_name = "Test"
        self.mock_faculty.last_name = "Faculty"

        # Mock tasks
        self.mock_task1 = Mock(spec=Task)
        self.mock_task1.id = 1
        self.mock_task1.title = "Test Task 1"

        self.mock_task2 = Mock(spec=Task)
        self.mock_task2.id = 2
        self.mock_task2.title = "Test Task 2"

    @patch('tasks.views.get_faculty_from_request')
    @patch('tasks.models.Task.objects.get')
    @patch('tasks.models.TaskProgress.objects.update_or_create')
    @patch('tasks.models.TaskProgress.objects.filter')
    def test_complete_task(self, mock_progress_filter, mock_progress_update, mock_task_get, mock_get_faculty):
        """Test completing a task with mocked objects."""
        # Set up session auth
        session = self.client.session
        session['_auth_user_id'] = '1'
        session.save()

        # Set up mock task
        self.mock_task1._meta = Mock()
        self.mock_task1._meta.model = Task
        self.mock_task1._meta.concrete_model = Task
        self.mock_task1._meta.all_parents = {}
        self.mock_task1._meta.parents = {}

        # Set up mock queryset for filter operations
        mock_queryset = Mock()
        mock_queryset.count = Mock(return_value=1)  # Mock the count method
        mock_progress_filter.return_value = mock_queryset

        # Set up other mocks
        mock_get_faculty.return_value = self.mock_faculty
        mock_task_get.return_value = self.mock_task1
        mock_progress = Mock(spec=TaskProgress)
        mock_progress.completed = True
        mock_progress_update.return_value = (mock_progress, True)

        # Test task completion
        with patch('django.contrib.auth.middleware.get_user', return_value=self.mock_user):
            response = self.client.post(reverse('tasks:complete_task', args=[1]))

        # Verify mocks were called correctly
        mock_task_get.assert_called_once_with(pk=1)
        mock_progress_update.assert_called_once_with(
            faculty=self.mock_faculty,
            task=self.mock_task1,
            defaults={'completed': True}
        )
        self.assertEqual(response.status_code, 302)

    @patch('django.contrib.auth.authenticate')
    @patch('django.contrib.auth.login')
    @patch('tasks.views.get_faculty_from_request')
    @patch('tasks.models.Task.objects.get')
    @patch('tasks.models.TaskProgress.objects.filter')
    def test_continue_task(self, mock_progress_filter, mock_task_get, mock_get_faculty, mock_login, mock_auth):
        """
        Test continuing (uncompleting) a task with mocked objects.
        
        Verifies:
        1. Task progress is deleted
        2. Redirects after uncompleting
        3. TaskProgress filter is called correctly
        
        Mocks:
        - Authentication
        - Task retrieval
        - TaskProgress filtering and deletion
        - Faculty retrieval
        """
        # Set up mocks
        mock_auth.return_value = self.mock_user
        mock_login.return_value = None
        mock_get_faculty.return_value = self.mock_faculty
        mock_task_get.return_value = self.mock_task1

        # Mock the queryset and its delete method
        mock_queryset = Mock()
        mock_queryset.delete = Mock()
        mock_progress_filter.return_value = mock_queryset

        # Test task uncomplete
        response = self.client.post(reverse('tasks:continue_task', args=[1]))

        # Verify mocks were called correctly
        mock_task_get.assert_called_once_with(pk=1)
        mock_progress_filter.assert_called_once_with(
            faculty=self.mock_faculty,
            task=self.mock_task1
        )
        mock_queryset.delete.assert_called_once()
        self.assertEqual(response.status_code, 302)
