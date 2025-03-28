from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Faculty
import uuid


class BasicUserTest(TestCase):
    """Basic test for user functionality"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class"""
        unique_id = str(uuid.uuid4()).replace('-', '')
        cls.username = f'testuser_{unique_id}'
        cls.email = f'test_{unique_id}@example.com'
        cls.test_user = User.objects.create_user(
            username=cls.username,
            email=cls.email,
            password='password123'
        )
        # Create the associated Faculty record expected by the profile view
        Faculty.objects.create(user=cls.test_user)
        
    def test_user_exists(self):
        """Verify that the test user was created correctly"""
        user = User.objects.get(username=self.username)
        self.assertEqual(user.email, self.email)
        
    def test_user_login(self):
        """Test that a user can login successfully"""
        client = Client()
        login_successful = client.login(username=self.username, password='password123')
        self.assertTrue(login_successful)
        
        # Access the profile page with following redirects
        response = client.get(reverse('users:profile'), follow=True)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, self.username)
        
    def test_logout(self):
        """Test that a user can logout successfully"""
        client = Client()
        client.login(username=self.username, password='password123')
        response = client.post(reverse('users:logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
    def test_invalid_login(self):
        """Test that login fails with invalid credentials"""
        client = Client()
        login_result = client.login(username=self.username, password='wrongpassword')
        self.assertFalse(login_result)
        
        # Unauthenticated access should redirect to login
        response = client.get(reverse('users:profile'), follow=True)
        self.assertEqual(response.resolver_match.url_name, 'login')
        
    def test_profile_access(self):
        """Test that profile page can be accessed and returns correct status code"""
        client = Client()
        client.login(username=self.username, password='password123')
        
        # Get profile page with following redirects
        response = client.get(reverse('users:profile'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile/details.html')


class AccessControlTest(TestCase):
    """Test access control to protected pages"""
    
    @classmethod
    def setUpTestData(cls):
        unique_id = str(uuid.uuid4()).replace('-', '')
        cls.regular_username = f'regular_{unique_id}'
        cls.regular_email = f'regular_{unique_id}@example.com'
        cls.regular_user = User.objects.create_user(
            username=cls.regular_username,
            email=cls.regular_email,
            password='password123'
        )
        # Create associated Faculty for the regular user
        Faculty.objects.create(user=cls.regular_user)
        
        cls.admin_username = f'admin_{unique_id}'
        cls.admin_email = f'admin_{unique_id}@example.com'
        cls.admin_user = User.objects.create_user(
            username=cls.admin_username,
            email=cls.admin_email,
            password='password123',
            is_staff=True,
            is_superuser=True
        )
        # Create associated Faculty for the admin user
        Faculty.objects.create(user=cls.admin_user)
    
    def test_profile_access_authentication(self):
        """Test that profile page requires authentication"""
        client = Client()
        response = client.get(reverse('users:profile'), follow=True)
        self.assertEqual(response.resolver_match.url_name, 'login')
        
        # After login, the profile page should be accessible
        client.login(username=self.regular_username, password='password123')
        response = client.get(reverse('users:profile'), follow=True)
        self.assertEqual(response.status_code, 200)
        
    def test_admin_access(self):
        """Test that admin interface requires staff permission"""
        client = Client()
        client.login(username=self.regular_username, password='password123')
        response = client.get('/admin/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('login', response.redirect_chain[0][0])
        
        # Admin user should access the admin interface
        client = Client()
        client.login(username=self.admin_username, password='password123')
        response = client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Site administration')


class RequestHandlingTest(TestCase):
    """Test HTTP request handling and status codes for various user interactions"""
    
    @classmethod
    def setUpTestData(cls):
        unique_id = str(uuid.uuid4()).replace('-', '')
        cls.username = f'reqtest_{unique_id}'
        cls.email = f'reqtest_{unique_id}@example.com'
        cls.password = 'testpassword123'
        cls.user = User.objects.create_user(
            username=cls.username,
            email=cls.email,
            password=cls.password
        )
        # Create associated Faculty for the test user
        Faculty.objects.create(user=cls.user)
    
    def test_login_get_request(self):
        """Test that GET request to login page returns login form"""
        client = Client()
        response = client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/auth/login.html')
        
    def test_login_post_request(self):
        """Test that POST request to login with valid credentials redirects appropriately"""
        client = Client()
        response = client.post(
            reverse('users:login'),
            {'username': self.username, 'password': self.password},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        
    def test_login_post_invalid_credentials(self):
        """Test that POST request with invalid credentials stays on the login page"""
        client = Client()
        response = client.post(
            reverse('users:login'),
            {'username': self.username, 'password': 'wrongpassword'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/auth/login.html')
        self.assertFalse(response.wsgi_request.user.is_authenticated)
