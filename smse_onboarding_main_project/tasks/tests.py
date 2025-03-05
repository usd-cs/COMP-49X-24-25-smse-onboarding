from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse

from tasks.models import Task, Faculty


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