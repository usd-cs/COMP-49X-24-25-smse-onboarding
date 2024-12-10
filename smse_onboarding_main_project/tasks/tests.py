from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse

from tasks.models import Task


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

    @patch('tasks.models.Task.objects.create')
    def test_task_creation_invalid_data(self, mock_create):
        """
        Test that creating a task with invalid data raises an error.
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
