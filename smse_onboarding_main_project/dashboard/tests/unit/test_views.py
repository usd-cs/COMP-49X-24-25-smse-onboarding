from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, Mock
from users.models import Faculty
from tasks.models import Task, TaskProgress

class DashboardViewTests(TestCase):
    """Unit tests for dashboard views with mocked models."""

    def setUp(self):
        """Set up test environment with mocked objects."""
        self.client = Client()

        # Mock user
        self.mock_user = Mock()
        self.mock_user.username = 'testuser'
        self.mock_user.is_authenticated = True
        self.mock_user.is_staff = False

        # Mock faculty
        self.mock_faculty = Mock(spec=Faculty)
        self.mock_faculty.user = self.mock_user
        self.mock_faculty.first_name = "Test"
        self.mock_faculty.last_name = "Faculty"

        # Mock task
        self.mock_task = Mock(spec=Task)
        self.mock_task.id = 1
        self.mock_task.title = "Test Task"
        self.mock_task.is_completed_by = Mock(return_value=False)
        self.mock_task.deadline = "2024-12-31"

        # Set up session auth
        session = self.client.session
        session['_auth_user_id'] = '1'
        session.save()

    # @patch('dashboard.views.get_faculty_from_request')
    # @patch('tasks.models.Task.objects.filter')
    # @patch('documents.models.FacultyDocument.objects.filter')
    # def test_new_hire_home(self, mock_docs_filter, mock_tasks_filter, mock_get_faculty):
    #     """Test new hire dashboard home view."""
    #     # Set up mock task with proper model metadata
    #     self.mock_task._meta = Mock()
    #     self.mock_task._meta.model = Task
    #     self.mock_task._meta.concrete_model = Task
    #     self.mock_task._meta.all_parents = set()
    #     self.mock_task._meta.parents = {}
    #
    #     # Set up mock queryset
    #     mock_tasks_filter.return_value = [self.mock_task]
    #     mock_docs_filter.return_value = []
    #     mock_get_faculty.return_value = self.mock_faculty
    #
    #     # Mock authentication
    #     with patch('django.contrib.auth.middleware.get_user', return_value=self.mock_user):
    #         response = self.client.get(reverse('dashboard:new_hire_home'))
    #
    #     mock_get_faculty.assert_called_once()
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'dashboard/new_hire/home.html')

    # @patch('dashboard.views.get_faculty_from_request')
    # @patch('tasks.models.Task.objects.get')
    # @patch('tasks.models.TaskProgress.objects.update_or_create')
    # @patch('django.contrib.messages.success')
    # def test_complete_task(self, mock_messages, mock_progress_update, mock_task_get, mock_get_faculty):
    #     """Test task completion from dashboard."""
    #     # Set up mock task with proper model metadata
    #     self.mock_task._meta = Mock()
    #     self.mock_task._meta.model = Task
    #     self.mock_task._meta.concrete_model = Task
    #     self.mock_task._meta.all_parents = set()
    #     self.mock_task._meta.parents = {}
    #
    #     mock_get_faculty.return_value = self.mock_faculty
    #     mock_task_get.return_value = self.mock_task
    #     mock_progress = Mock(spec=TaskProgress)
    #     mock_progress_update.return_value = (mock_progress, True)
    #
    #     # Mock authentication
    #     with patch('django.contrib.auth.middleware.get_user', return_value=self.mock_user):
    #         response = self.client.post(reverse('dashboard:complete_task', args=[1]))
    #
    #     mock_task_get.assert_called_once_with(pk=1)
    #     mock_progress_update.assert_called_once()
    #     mock_messages.assert_called_once()
    #     self.assertEqual(response.status_code, 302)

    # @patch('dashboard.views.get_faculty_from_request')
    # @patch('tasks.models.Task.objects.all')
    # @patch('documents.models.FacultyDocument.objects.filter')
    # def test_admin_home(self, mock_docs_filter, mock_tasks_all, mock_get_faculty):
    #     """Test admin dashboard home view."""
    #     # Set up mock task with proper model metadata
    #     self.mock_task._meta = Mock()
    #     self.mock_task._meta.model = Task
    #     self.mock_task._meta.concrete_model = Task
    #     self.mock_task._meta.all_parents = set()
    #     self.mock_task._meta.parents = {}
    #
    #     # Set up staff user
    #     self.mock_user.is_staff = True
    #     mock_get_faculty.return_value = self.mock_faculty
    #     mock_tasks_all.return_value = [self.mock_task]
    #     mock_docs_filter.return_value = []
    #
    #     # Mock authentication with staff user
    #     with patch('django.contrib.auth.middleware.get_user', return_value=self.mock_user):
    #         response = self.client.get(reverse('dashboard:admin_home'))
    #
    #     mock_get_faculty.assert_called_once()
    #     mock_tasks_all.assert_called_once()
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'dashboard/admin/home.html')
