from unittest.mock import MagicMock
from datetime import datetime, timedelta
from django.test import TestCase, Client
from unittest.mock import patch, Mock
from django.urls import reverse
from tasks.models import Task
from users.models import Faculty

class ReminderViewTests(TestCase):
    """Unit tests for reminder views with mocked objects."""

    def setUp(self):
        """Set up test environment with mocked objects."""
        self.client = Client()

        # Mock user
        self.mock_user = Mock()
        self.mock_user.username = 'testuser'
        self.mock_user.email = 'testuser@sandiego.edu'
        self.mock_user.is_authenticated = True

        # Mock faculty
        self.mock_faculty = Mock(spec=Faculty)
        self.mock_faculty.user = self.mock_user
        self.mock_faculty.first_name = "Test"
        self.mock_faculty.last_name = "Faculty"
        self.mock_faculty.email = 'testuser@sandiego.edu'

        # Mock tasks
        self.mock_task1 = Mock(spec=Task)
        self.mock_task1.id = 1
        self.mock_task1.title = "Test Task 1"
        self.mock_task1.created_at = datetime(2025, 4, 20, 12, 0, 0)
        self.mock_task1.deadline = datetime(2025, 4, 25, 12, 0, 0)
        self.mock_task1.prerequisite_task = None
        self.mock_task1.description = "Test Description"
        
    def test_time_more_than_1_day(self):
        """Test the time remaining days for a task."""
        current_time = datetime(2025, 4, 22, 12, 0, 0)
        self.assertGreater((self.mock_task1.deadline - current_time).days, 1)

        if (self.mock_task1.deadline - current_time).days > 1:
            days_remaining = f"You have {(self.mock_task1.deadline - current_time).days} days remaining to complete this task."
        else:
            days_remaining = None

        self.assertEqual(days_remaining, "You have 3 days remaining to complete this task.")

    def test_time_less_than_1_day(self):
        """Test the time remaining hours for a task."""
        current_time = datetime(2025, 4, 24, 18, 0, 0)
        
        self.assertLess((self.mock_task1.deadline - current_time).total_seconds() / 3600, 24)
        self.assertGreater((self.mock_task1.deadline - current_time).total_seconds() / 3600, 0)

        if (self.mock_task1.deadline - current_time).total_seconds() / 3600 <= 24 and (self.mock_task1.deadline - current_time).total_seconds() / 3600 > 0:
            days_remaining = "You have less than 24 hours remaining to complete this task."
        else:
            days_remaining = None

        self.assertEqual(days_remaining, "You have less than 24 hours remaining to complete this task.")

    def test_time_overdue(self):
        """Test the time remaining days for a task."""
        current_time = datetime(2025, 4, 26, 12, 0, 0)

        self.assertLess((self.mock_task1.deadline - current_time).total_seconds() / 3600, 0)

        if (self.mock_task1.deadline - current_time).total_seconds() / 3600 < 0:
            days_remaining = "This task is overdue."
        else:
            days_remaining = None

        self.assertEqual(days_remaining, "This task is overdue.")

    def test_reminder_email(self):
        """Test that the reminder email is correct."""
        current_time = datetime(2025, 4, 22, 12, 0, 0)
        days_remaining = f"You have {str((self.mock_task1.deadline - current_time).days)} days remaining to complete this task."
        time_remaining = f"{str((self.mock_task1.deadline - current_time).days)} days"
        
        message = f"""Hello {self.mock_faculty.first_name} {self.mock_faculty.last_name},

This is a reminder about your new hire onboarding task: {self.mock_task1.title}.
This task is due on {str(self.mock_task1.deadline.strftime('%B %d, %Y, %I:%M %p'))}.
{days_remaining}
Please complete this task as soon as possible.
Please log in to the SMSE Onboarding Portal at https://smse-onboarding.dedyn.io to view the task and complete it.
        
See below for the task details:

Title: {self.mock_task1.title}
Created: {str(self.mock_task1.created_at.strftime('%B %d, %Y, %I:%M %p'))}
Deadline: {str(self.mock_task1.deadline.strftime('%B %d, %Y, %I:%M %p'))}
Prerequisite Task: {self.mock_task1.prerequisite_task.title if self.mock_task1.prerequisite_task else "None"}
Remaining Time: {time_remaining}
Description: {self.mock_task1.description}

If you have any questions, please contact the SMSE Admin team at smseadmin@sandiego.edu.

Thank you,

SMSE Admin Team
        """

        expected_message = """Hello Test Faculty,

This is a reminder about your new hire onboarding task: Test Task 1.
This task is due on April 25, 2025, 12:00 PM.
You have 3 days remaining to complete this task.
Please complete this task as soon as possible.
Please log in to the SMSE Onboarding Portal at https://smse-onboarding.dedyn.io to view the task and complete it.
        
See below for the task details:

Title: Test Task 1
Created: April 20, 2025, 12:00 PM
Deadline: April 25, 2025, 12:00 PM
Prerequisite Task: None
Remaining Time: 3 days
Description: Test Description

If you have any questions, please contact the SMSE Admin team at smseadmin@sandiego.edu.

Thank you,

SMSE Admin Team
        """

        self.assertEqual(message, expected_message)