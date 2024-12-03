from django.test import TestCase

from smse_onboarding.models import Faculty, Task, TaskProgress


class FacultyModelTest(TestCase):
    def setUp(self):
        # Create sample data for testing
        self.faculty = Faculty.objects.create(
            first_name="Jane",
            last_name="Doe",
            job_role="Professor",
            engineering_dept="Computer Science",
            password="securepassword",
            email="jane.doe@example.com",
            phone="1234567890",
            zoom_phone="0987654321",
            office_room="CS101",
            hire_date="2024-01-01T09:00:00Z",
            mailing_list_status=True,
            bio="Experienced computer science professor."
        )

    def test_faculty_creation(self):
        # Test if faculty was created successfully
        self.assertEqual(self.faculty.first_name, "Jane")
        self.assertEqual(self.faculty.last_name, "Doe")
        self.assertEqual(self.faculty.engineering_dept, "Computer Science")


class TaskModelTest(TestCase):
    def setUp(self):
        # Create a faculty member for testing relationships
        self.faculty = Faculty.objects.create(
            first_name="John",
            last_name="Smith",
            job_role="Assistant Professor",
            engineering_dept="Electrical Engineering",
            password="password123",
            email="john.smith@example.com",
            phone="9876543210",
            zoom_phone="0123456789",
            office_room="EE102",
            hire_date="2024-01-02T09:00:00Z",
            mailing_list_status=False,
            bio="New hire in Electrical Engineering."
        )

        # Create a task for testing
        self.task = Task.objects.create(
            task_name="Setup Email",
            due_date="2024-02-01T10:00:00Z",
            created_date="2024-01-01T10:00:00Z",
            completed_status=False,
            assigned_to="John Smith",
            description="Set up your university email account."
        )

    def test_task_creation(self):
        # Test if task was created successfully
        self.assertEqual(self.task.task_name, "Setup Email")
        self.assertFalse(self.task.completed_status)
        self.assertEqual(self.task.description, "Set up your university email account.")

    def test_task_progress(self):
        # Test TaskProgress creation
        progress = TaskProgress.objects.create(
            faculty=self.faculty,
            task=self.task,
            progress_status="In Progress"
        )
        self.assertEqual(progress.progress_status, "In Progress")
        self.assertEqual(progress.task.task_name, "Setup Email")
        self.assertEqual(progress.faculty.first_name, "John")
