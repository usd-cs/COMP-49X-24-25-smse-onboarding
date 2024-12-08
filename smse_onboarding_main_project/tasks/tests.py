from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Task


class TaskTests(TestCase):
    """
    Setting up the test case.
    """

    def setUp(self):
        self.task = Task.objects.create(
            title="Test Task",
            description="This is a test task.",
            deadline=timezone.now() + timedelta(days=30),  # using timezone-aware datetime
            completed=False,
        )

    """
    Test case for completing a task
    """

    def test_complete_task_success(self):
        # mocks completing a task
        response = self.client.post(reverse('tasks:complete_task', args=[self.task.id]))
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.task.completed)
        # self.assertEqual(response.json()['message'], f'Task "{self.task.title}" marked as completed successfully!')

    """
    Test case for mocking a save.
    """
    @patch('tasks.models.Task.save')  # mocks the save method
    def test_complete_task_mock_save(self, mock_save):
        # mocks completing a task with a mocked save
        response = self.client.post(reverse('tasks:complete_task', args=[self.task.id]))
        mock_save.assert_called_once()
        self.assertEqual(response.status_code, 302)
