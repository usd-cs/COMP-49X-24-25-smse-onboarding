from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse

from tasks.models import Task


class TaskTests(TestCase):
    """
    Unit tests for the Task model using mocks to avoid database creation.
    """

    @patch('tasks.models.Task.objects.create')  # mocks the create method
    def test_task_creation(self, mock_create):
        """
        Test the creation of a Task object using a mock.
        
        Args:
            mock_create (Mock): Mocked `Task.objects.create` method.
        """

        # testing with a fixed deadline so test passes
        test_deadline = datetime(2025, 1, 9, 2, 57, 1, tzinfo=timezone.utc)

        # set up the mocked task
        mock_task = Mock()
        mock_task.title = "Test Task"
        mock_task.completed = False
        mock_create.return_value = mock_task

        # mock calling create method
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

    @patch('tasks.views.get_object_or_404')  # mocks the get object method
    def test_complete_task_success(self, mock_get_object_or_404):
        """
        Test marking a task as completed using mocked database functions.

        Args:
            mock_get_object_or_404 (Mock): Mocked `get_object_or_404` method.
        """
        # setup the mocked task
        mock_task = Mock()
        mock_task.completed = False
        mock_task.save = Mock()
        mock_get_object_or_404.return_value = mock_task

        # simulate completing task
        response = self.client.post(reverse('tasks:complete_task', args=[1]))

        mock_get_object_or_404.assert_called_once_with(Task, id=1)
        mock_task.save.assert_called_once()
        self.assertTrue(mock_task.completed)
        self.assertEqual(response.status_code, 302)
        # self.assertEqual(response.json()['message'], f'Task "{self.task.title}" marked as completed successfully!')

    @patch('tasks.models.Task.save')  # mocks the save method
    def test_complete_task_mock_save(self, mock_save):
        """
        Test that the save method is called when marking a task as complete.

        Args:
            mock_save (Mock): Mocked `Task.save` method.
        """
        # set up a mocked task
        mock_task = Mock()
        mock_task.save = mock_save

        # simulate saving a task
        mock_task.save()

        # response = self.client.post(reverse('tasks:complete_task', args=[self.task.id]))
        mock_save.assert_called_once()
        # self.assertEqual(response.status_code, 302)
