from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User, Group
from users.models import Faculty
from django.utils import timezone
from unittest.mock import patch, Mock, MagicMock
from django.contrib.messages.storage.fallback import FallbackStorage
from io import BytesIO
from PIL import Image
import tempfile

def create_test_image():
    """Helper function to create a test image file."""
    image_file = BytesIO()
    Image.new('RGB', (100, 100), color='red').save(image_file, 'JPEG')
    image_file.name = 'test_image.jpg'
    image_file.seek(0)
    return image_file

class UserViewTests(TestCase):
    """Unit tests for user-related views with mocked models."""

    def setUp(self):
        """Set up test environment with mocked objects."""
        self.client = Client()
        self.factory = RequestFactory()

        # Create a real user for tests that need it
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

        # Create mock regular (non-admin) user
        self.mock_regular_user = Mock(spec=User)
        self.mock_regular_user.username = 'testuser'
        self.mock_regular_user.is_authenticated = True
        self.mock_regular_user.is_staff = False
        self.mock_regular_user.is_superuser = False
        self.mock_regular_user.is_active = True
        self.mock_regular_user.get_full_name.return_value = "Test User"
        self.mock_regular_user.email = "test@example.com"

        # Create mock admin (staff) user
        self.mock_staff_user = Mock(spec=User)
        self.mock_staff_user.username = 'staffuser'
        self.mock_staff_user.is_authenticated = True
        self.mock_staff_user.is_staff = True
        self.mock_staff_user.is_superuser = False
        self.mock_staff_user.is_active = True
        self.mock_staff_user.get_full_name.return_value = "Staff User"
        self.mock_staff_user.email = "staff@example.com"

        # Create mock faculty
        self.mock_faculty = Mock(spec=Faculty)
        self.mock_faculty.first_name = "Test"
        self.mock_faculty.last_name = "Faculty"
        self.mock_faculty.email = "test@sandiego.edu"
        self.mock_faculty.profile_image = None
        self.mock_faculty.job_role = "Faculty Member"
        self.mock_faculty.office_room = "Office 123"
        self.mock_faculty.bio = "Test bio"

    @patch('users.models.Faculty.objects.get')
    def test_profile_view(self, mock_get_faculty):
        """Test profile view with mocked faculty query."""
        # Set up session auth
        self.client.force_login(self.user)

        # Set up faculty mock
        mock_get_faculty.return_value = self.mock_faculty

        # Mock the user authentication
        with patch('django.contrib.auth.middleware.get_user', return_value=self.user):
            response = self.client.get(reverse('users:profile'))

            # Verify the faculty was retrieved - use assert_called instead of assert_called_once
            mock_get_faculty.assert_called()
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'users/profile/details.html')

    @patch('django.shortcuts.redirect')
    def test_dismiss_welcome_banner_with_referer(self, mock_redirect):
        """Test dismiss_welcome_banner view sets session variable and redirects."""
        # Set up session auth
        self.client.force_login(self.user)
        session = self.client.session
        session['show_welcome_banner'] = True
        session.save()

        # Set up return URL
        referer_url = 'http://testserver/dashboard/'

        # Make the request
        response = self.client.get(
            reverse('users:dismiss_welcome'),
            HTTP_REFERER=referer_url
        )

        # Check if session variable is set to False
        self.assertFalse(self.client.session.get('show_welcome_banner'))

        # Should redirect to the referer URL
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, referer_url)

    @patch('django.shortcuts.redirect')
    def test_show_welcome_with_referer(self, mock_redirect):
        """Test show_welcome view sets session variable and redirects."""
        # Set up session auth
        self.client.force_login(self.user)
        session = self.client.session
        session['show_welcome_banner'] = False
        session.save()

        # Set up return URL
        referer_url = 'http://testserver/dashboard/'

        # Make the request
        response = self.client.get(
            reverse('users:show_welcome'),
            HTTP_REFERER=referer_url
        )

        # Check if session variable is set to True
        self.assertTrue(self.client.session.get('show_welcome_banner'))

        # Should redirect to the referer URL
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, referer_url)

    def test_welcome_info_view(self):
        """Test welcome_info view renders the correct template."""
        # Set up user authentication
        self.client.force_login(self.user)

        # Make the request
        response = self.client.get(reverse('users:welcome_info'))

        # Should return 200 OK
        self.assertEqual(response.status_code, 200)

        # Should use the newhire_help_guide.html template
        self.assertTemplateUsed(response, 'users/newhire_help_guide.html')

    def test_admin_help_guide_view(self):
        """Test admin_help_guide view renders the correct template."""
        # Set up user authentication
        self.client.force_login(self.user)

        # Make the request
        response = self.client.get(reverse('users:admin_help_guide'))

        # Should return 200 OK
        self.assertEqual(response.status_code, 200)

        # Should use the admin_help_guide.html template
        self.assertTemplateUsed(response, 'users/admin_help_guide.html')

    # Tests for the update_profile functionality
    @patch('users.models.Faculty.objects.get')
    def test_update_profile_unauthorized(self, mock_get_faculty):
        """Test update_profile requires authentication."""
        # Try to access without being logged in
        response = self.client.post(reverse('users:update_profile'), {
            'username': 'newusername',
            'job_role': 'New Role',
            'office': 'New Office',
            'bio': 'This is a new bio'
        })

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login' in response.url)

        # Faculty get should not be called
        mock_get_faculty.assert_not_called()

    @patch('users.models.Faculty.objects.get')
    def test_update_profile_success(self, mock_get_faculty):
        """Test successful profile update with all fields."""
        # Set up user authentication
        self.client.force_login(self.user)

        # Create a faculty object for this test
        faculty = MagicMock(spec=Faculty)
        faculty.job_role = 'Old Role'
        faculty.office_room = 'Old Office'
        faculty.bio = None
        faculty.profile_image = None

        # Mock the faculty get to return our object
        mock_get_faculty.return_value = faculty

        # Submit the form with updated data
        response = self.client.post(
            reverse('users:update_profile'),
            {
                'username': 'newusername',
                'job_role': 'New Role',
                'office': 'New Office',
                'bio': 'This is a test bio'
            },
            HTTP_REFERER='http://testserver/dashboard/'
        )

        # Should redirect back to the referer
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://testserver/dashboard/')

        # Verify the faculty was retrieved
        mock_get_faculty.assert_called_once()

        # Check that the values were updated
        self.assertEqual(faculty.job_role, 'New Role')
        self.assertEqual(faculty.office_room, 'New Office')
        self.assertEqual(faculty.bio, 'This is a test bio')

        # Verify save was called
        faculty.save.assert_called_once()

    @patch('users.models.Faculty.objects.get')
    def test_update_profile_image_upload(self, mock_get_faculty):
        """Test profile image upload functionality."""
        # Set up user authentication
        self.client.force_login(self.user)

        # Create a faculty object
        faculty = MagicMock(spec=Faculty)
        faculty.profile_image = None

        # Mock the faculty get to return our object
        mock_get_faculty.return_value = faculty

        # Create a test image file
        image_file = create_test_image()

        # Submit the form with the image file
        response = self.client.post(
            reverse('users:update_profile'),
            {
                'profile_picture': image_file
            },
            HTTP_REFERER='http://testserver/dashboard/'
        )

        # Should redirect back to the referer
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://testserver/dashboard/')

        # Verify faculty.save was called
        faculty.save.assert_called_once()

