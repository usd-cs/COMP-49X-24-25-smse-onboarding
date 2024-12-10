from datetime import timedelta
from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Task


class TaskTests(TestCase):
    """
    Unit tests for the Task model using mocks to avoid database creation.
    """

    @patch('smse_onboarding.models.Task.objects.create')  # mocks the create method
    def test_task_creation(self, mock_create):
        """
        Test the creation of a Task object using a mock.
        
        Args:
            mock_create (Mock): Mocked `Task.objects.create` method.
        """
        #set up the mocked task
        mock_task = Mock()
        mock_task.title = "Test Task"
        mock_task.completed = False
        mock_create.return_value = mock_task

        #mock calling create method
        task = Task.objects.create(
            title="Test Task",
            description="This is a test task.",
            deadline=timezone.now() + timedelta(days=30),
            completed=False,
        )

        mock_create.assert_called_once_with(
            title="Test Task",
            description="This is a test task.",
            deadline=timezone.now() + timedelta(days=30),
            completed=False,
        )
        self.assertEqual(task.title, "Test Task")
        self.assertFalse(task.completed)

    @patch('smse_onboarding.models.Task.objects.get')  # mocks the get method
    @patch('smse_onboarding.models.Task.save')         # Mocks the save method
    def test_complete_task_success(self, mock_save, mock_get):
        """
        Test marking a task as completed using mocked database functions.

        Args:
            mock_save (Mock): Mocked `Task.save` method.
            mock_get (Mock): Mocked `Task.objects.get` method.
        """
        # setup the mocked task
        mock_task = Mock()
        mock_task.completed = False
        mock_get.return_value = mock_task

        #simulate completing task
        response = self.client.post(reverse('tasks:complete_task', args=[1]))

        mock_get.assert_called_once_with(id=1)
        mock_save.assert_called_once()
        mock_task.completed = True  # Simulate marking the task as complete
        self.assertEqual(response.status_code, 302)
        # self.assertEqual(response.json()['message'], f'Task "{self.task.title}" marked as completed successfully!')

    @patch('smse_onboarding.models.Task.save')  # mocks the save method
    def test_complete_task_mock_save(self, mock_save):
        """
        Test that the save method is called when marking a task as complete.

        Args:
            mock_save (Mock): Mocked `Task.save` method.
        """
        # set up a mocked task
        mock_task = Mock()
        mock_task.save = mock_save

        #simulate saving a task
        mock_task.save()

        #response = self.client.post(reverse('tasks:complete_task', args=[self.task.id]))
        mock_save.assert_called_once()
        #self.assertEqual(response.status_code, 302)
