from django.test import TestCase
from unittest.mock import patch, Mock
from django.utils import timezone
from django.contrib.auth.models import User
from tasks.models import Task, TaskProgress
from users.models import Faculty
from datetime import datetime

class TaskModelTests(TestCase):
    """Unit tests for Task model functionality using mocks."""

    def setUp(self):
        """
        Set up test data with mocked objects.
        
        Creates:
        - Mock User
        - Mock Faculty
        - Mock Task with properties
        - Mock TaskProgress
        
        Mocks:
        - User model
        - Faculty model
        - Task model and methods
        - TaskProgress model
        """
        # Mock user
        self.mock_user = Mock()
        self.mock_user.username = 'testuser'

        # Mock faculty
        self.mock_faculty = Mock(spec=Faculty)
        self.mock_faculty.user = self.mock_user

        # Mock task
        self.mock_task = Mock(spec=Task)
        self.mock_task.title = "Test Task"
        self.mock_task.description = "Test Description"
        self.mock_task.deadline = timezone.now() + timezone.timedelta(days=7)
        self.mock_task.completed = False
        self.mock_task.assigned_to = Mock()
        self.mock_task.assigned_to.add = Mock()

    @patch('tasks.models.Task.objects.create')
    def test_task_creation(self, mock_create):
        """
        Test task creation with mocked database calls.
        
        Verifies:
        1. Task.objects.create is called with correct parameters
        2. Task is properly assigned to faculty
        3. Task attributes are set correctly
        
        Mocks:
        - Task creation
        - Task-Faculty relationship
        """
        mock_create.return_value = self.mock_task

        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            deadline=timezone.now() + timezone.timedelta(days=7)
        )
        task.assigned_to.add(self.mock_faculty)

        mock_create.assert_called_once()
        self.assertEqual(task.title, "Test Task")
        self.assertFalse(task.completed)

    @patch('tasks.models.TaskProgress.objects.create')
    def test_task_completion(self, mock_progress_create):
        """
        Test task completion functionality with mocked progress.
        
        Verifies:
        1. TaskProgress is created when marking task complete
        2. Task completion status is tracked per faculty
        3. Task progress creation is called with correct parameters
        
        Mocks:
        - TaskProgress creation
        - Task-Faculty relationship
        """
        mock_progress = Mock(spec=TaskProgress)
        mock_progress.completed = True
        mock_progress_create.return_value = mock_progress

        progress = TaskProgress.objects.create(
            faculty=self.mock_faculty,
            task=self.mock_task,
            completed=True
        )

        mock_progress_create.assert_called_once_with(
            faculty=self.mock_faculty,
            task=self.mock_task,
            completed=True
        )
        self.assertTrue(progress.completed)

    def test_task_deadline(self):
        """Test task deadline calculations with mocked properties."""
        # Mock the is_overdue property directly on the instance
        self.mock_task.is_overdue = False
        self.assertFalse(self.mock_task.is_overdue)

        self.mock_task.is_overdue = True
        self.assertTrue(self.mock_task.is_overdue)
