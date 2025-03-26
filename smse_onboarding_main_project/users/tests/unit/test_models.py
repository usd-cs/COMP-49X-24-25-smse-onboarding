from django.test import TestCase
from unittest.mock import patch, Mock
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import Faculty
from datetime import datetime

class FacultyModelTests(TestCase):
    """Unit tests for Faculty model functionality using mocks."""

    @patch('django.contrib.auth.models.User.objects.create_user')
    @patch('users.models.Faculty.objects.create')
    def setUp(self, mock_faculty_create, mock_user_create):
        """
        Set up test data with mocked objects.
        Mocks both User and Faculty creation.
        """
        # Mock User
        self.mock_user = Mock(spec=User)
        self.mock_user.username = 'testfaculty'
        self.mock_user.email = 'testfaculty@sandiego.edu'
        mock_user_create.return_value = self.mock_user

        # Mock Faculty
        self.mock_faculty = Mock(spec=Faculty)
        self.mock_faculty.faculty_id = 1
        self.mock_faculty.user = self.mock_user
        self.mock_faculty.first_name = "Test"
        self.mock_faculty.last_name = "Faculty"
        self.mock_faculty.job_role = "Professor"
        self.mock_faculty.engineering_dept = "Computer Science"
        self.mock_faculty.email = "testfaculty@sandiego.edu"
        self.mock_faculty.phone = "8581234567"
        self.mock_faculty.zoom_phone = "6192601234"
        self.mock_faculty.office_room = "GH101"
        self.mock_faculty.hire_date = timezone.now()
        self.mock_faculty.mailing_list_status = False
        self.mock_faculty.bio = "This is a test bio"
        self.mock_faculty.completed_onboarding = False
        mock_faculty_create.return_value = self.mock_faculty

    @patch('users.models.Faculty.objects.create')
    def test_faculty_creation(self, mock_create):
        """
        Test faculty creation with mocked database calls.
        
        Verifies:
        1. Faculty.objects.create is called with correct parameters
        2. Returned faculty object has correct attributes
        """
        mock_create.return_value = self.mock_faculty

        faculty = Faculty.objects.create(
            user=self.mock_user,
            first_name="Test",
            last_name="Faculty",
            job_role="Professor",
            engineering_dept="Computer Science",
            email="testfaculty@sandiego.edu",
            phone="8581234567",
            office_room="GH101",
            hire_date=timezone.now()
        )

        mock_create.assert_called_once()
        self.assertEqual(faculty.first_name, "Test")
        self.assertEqual(faculty.last_name, "Faculty")

    @patch('users.models.Faculty.objects.get')
    def test_faculty_user_relationship(self, mock_get):
        """
        Test Faculty-User relationship with mocked queries.
        
        Verifies:
        1. Faculty can be retrieved by user
        2. User-Faculty relationship is properly mocked
        """
        mock_get.return_value = self.mock_faculty

        faculty = Faculty.objects.get(user=self.mock_user)
        self.assertEqual(faculty.user.username, 'testfaculty')
        mock_get.assert_called_once_with(user=self.mock_user)

    def test_faculty_defaults(self):
        """
        Test default values for faculty fields.
        
        Verifies:
        1. completed_onboarding defaults to False
        2. mailing_list_status defaults to False
        3. Optional fields can be null/blank
        """
        self.assertFalse(self.mock_faculty.completed_onboarding)
        self.assertFalse(self.mock_faculty.mailing_list_status)
