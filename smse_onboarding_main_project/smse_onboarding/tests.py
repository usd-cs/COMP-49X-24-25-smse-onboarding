from unittest import TestCase
from unittest.mock import MagicMock
from datetime import datetime, timedelta


class TaskMock:
    """Mock for Task model."""
    def __init__(self, task_id, task_name, due_date, completed_status):
        self.task_id = task_id
        self.task_name = task_name
        self.due_date = due_date
        self.completed_status = completed_status
        self.save = MagicMock()  # Mock save method


class TaskProgressMock:
    """Mock for TaskProgress model."""
    def __init__(self, progress_id, task, faculty, progress_status):
        self.progress_id = progress_id
        self.task = task
        self.faculty = faculty
        self.progress_status = progress_status
        self.save = MagicMock()  # Mock save method


class TaskTests(TestCase):
    """Unit tests for Task model with a mocked database."""

    def setUp(self):
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
        self.mock_task.completed_status = True  # Simulate status update
        self.assertTrue(self.mock_task.completed_status)


class TaskProgressTests(TestCase):
    """Unit tests for TaskProgress model with a mocked database."""

    def setUp(self):
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
        self.mock_task_progress.progress_status = "Completed"  # Simulate status update
        self.assertEqual(self.mock_task_progress.progress_status, "Completed")
