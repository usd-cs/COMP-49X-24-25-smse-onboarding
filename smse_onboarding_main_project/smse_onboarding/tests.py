from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import MagicMock


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
        self.mock_task.completed_status = True  # Simulate status update
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
        self.mock_task_progress.progress_status = "Completed"  # Simulate status update
        self.assertEqual(self.mock_task_progress.progress_status, "Completed")
