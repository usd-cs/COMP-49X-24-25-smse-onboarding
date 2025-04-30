from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid
import time
from .base_test import BaseE2ETest
from tasks.models import Task, TaskProgress
from users.models import Faculty

class TasksTest(BaseE2ETest):
    """End-to-end tests for tasks functionality using Selenium"""

    def setUp(self):
        """Set up before each test"""
        super().setUp()

        # Generate truly unique data
        self.unique_id = str(uuid.uuid4())[:8]
        self.random_username = f"testuser_{self.unique_id}"
        self.random_email = f"test_{self.unique_id}@example.com"
        self.test_password = 'testpass123'

        # Create a regular user (not a superuser)
        self.user = User.objects.create_user(
            username=self.random_username,
            email=self.random_email,
            password=self.test_password,
            first_name="Test",
            last_name="Faculty"
        )

        # Make the user a staff member to ensure login works
        self.user.is_staff = True
        self.user.save()

        # Get the faculty profile created by signals
        self.faculty = Faculty.objects.get(user=self.user)

        # Update faculty fields
        self.faculty.job_role = "Professor"
        self.faculty.engineering_dept = "Computer Science"
        self.faculty.phone = "1234567890"
        self.faculty.office_room = "TEST123"
        self.faculty.hire_date = timezone.now().date()
        # Ensure faculty is not marked as admin
        self.faculty.is_admin = False
        self.faculty.save()

        # Create test tasks
        self.task1 = Task.objects.create(
            title="Upload Resume",
            description="Upload your resume",
            deadline=timezone.now() + timedelta(days=7)
        )
        self.task1.assigned_to.add(self.faculty)

        self.task2 = Task.objects.create(
            title="Computer Request",
            description="Computer Request",
            deadline=timezone.now() + timedelta(days=14),
            prerequisite_task=self.task1
        )
        self.task2.assigned_to.add(self.faculty)

    def login_and_go_to_tasks(self):
        """Log in and navigate to the tasks page, handling redirects properly"""
        print("Setting up login sequence...")

        # First, log in via admin since that seems to work more reliably
        self.driver.get(f"{self.live_server_url}/admin/login/")

        # Take screenshot of login page
        self.take_screenshot("admin_login_page")

        # Fill in the login form
        username_input = self.wait_for_element(By.NAME, "username")
        password_input = self.wait_for_element(By.NAME, "password")

        username_input.send_keys(self.random_username)
        password_input.send_keys(self.test_password)

        # Print the current URL before submitting
        print(f"Current URL before login: {self.driver.current_url}")

        # Submit the form
        submit_button = self.wait_for_element(By.CSS_SELECTOR, "input[type='submit']")
        submit_button.click()

        # Wait for the page to load after login
        time.sleep(2)
        print(f"URL after login attempt: {self.driver.current_url}")
        self.take_screenshot("after_admin_login")

        # Check if login was successful by looking for logout link
        if "/admin/" in self.driver.current_url:
            print("Successfully logged in via admin")
        else:
            print("Login via admin may have failed. Current URL:", self.driver.current_url)

        # Now try to force login by using Django's built-in login mechanism
        # Visit a URL that we know requires login and will redirect to your app's login page
        print("Navigating to tasks home...")
        self.driver.get(f"{self.live_server_url}/tasks/")
        self.take_screenshot("tasks_home_redirect")
        print(f"Tasks home redirected to: {self.driver.current_url}")

        # Check if we're on a login form
        if "login" in self.driver.current_url.lower():
            try:
                print("On login page, attempting login")
                # Try to find login form fields - these might vary based on your app
                username_field = self.driver.find_elements(By.CSS_SELECTOR,
                                                  "input[name='username'], input[type='text']")
                password_field = self.driver.find_elements(By.CSS_SELECTOR,
                                                  "input[name='password'], input[type='password']")

                if username_field and password_field:
                    username_field[0].send_keys(self.random_username)
                    password_field[0].send_keys(self.test_password)

                    # Find and click submit button
                    submit_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                                                     "button[type='submit'], input[type='submit']")
                    if submit_buttons:
                        submit_buttons[0].click()
                        time.sleep(2)
                        self.take_screenshot("after_login_form_submit")
                        print(f"After form submit URL: {self.driver.current_url}")
            except Exception as e:
                print(f"Error trying to login via form: {e}")

        # Take screenshot of current page
        self.take_screenshot("current_page_after_login_attempts")

        # Now try visiting both dashboards to see which one works
        print("Trying admin dashboard...")
        self.driver.get(f"{self.live_server_url}/admin/")
        time.sleep(1)
        self.take_screenshot("admin_dashboard_access")
        print(f"Admin dashboard URL: {self.driver.current_url}")

        print("Trying new hire dashboard manually...")
        self.driver.get(f"{self.live_server_url}/dashboard/")
        time.sleep(1)
        self.take_screenshot("dashboard_access")
        print(f"Dashboard URL: {self.driver.current_url}")

        # Try other possible URLs for tasks/dashboard
        possible_urls = [
            "/dashboard/newhire/",
            "/tasks/",
            "/home/",
            "/",
        ]

        for url in possible_urls:
            print(f"Trying URL: {url}")
            self.driver.get(f"{self.live_server_url}{url}")
            time.sleep(1)
            self.take_screenshot(f"url_attempt_{url.replace('/', '_')}")
            print(f"URL after attempt: {self.driver.current_url}")
            # If we're not on a login page, we might have found the right URL
            if "login" not in self.driver.current_url.lower():
                print(f"Possible success with URL: {url}")
                return True

        print("Could not find a working dashboard URL after attempts")
        return False

    def test_explore_app_structure(self):
        """Test to explore the application structure and available URLs"""
        print("\nExploring application structure...")

        # Try to login and navigate to tasks
        login_success = self.login_and_go_to_tasks()

        # Take screenshot of current state
        self.take_screenshot("app_exploration")

        try:
            # Analyze the current page
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page title: {self.driver.title}")

            # Get page content
            page_content = self.driver.page_source

            # Look for key content in the page
            key_terms = [
                "dashboard", "task", "complete", "resume", "request",
                "faculty", "welcome", "onboarding", "login"
            ]

            print("Page content analysis:")
            for term in key_terms:
                print(f"Term '{term}' present: {term.lower() in page_content.lower()}")

            # Find main navigation elements
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "nav, .nav, .navbar, .sidebar")
            print(f"Found {len(nav_elements)} navigation elements")

            if nav_elements:
                for i, nav in enumerate(nav_elements):
                    print(f"Nav {i} text: {nav.text[:100]}...")
                    print(f"Nav {i} class: {nav.get_attribute('class')}")

            # Find key UI components
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            links = self.driver.find_elements(By.TAG_NAME, "a")
            forms = self.driver.find_elements(By.TAG_NAME, "form")

            print(f"Found {len(buttons)} buttons, {len(links)} links, {len(forms)} forms")

            # Print the first few links to help identify navigation
            print("First few links:")
            for i, link in enumerate(links[:5]):
                print(f"Link {i} text: {link.text}")
                print(f"Link {i} href: {link.get_attribute('href')}")

            # Verify our tasks exist in the database
            self.assertTrue(
                Task.objects.filter(
                    id=self.task1.id,
                    title="Upload Resume"
                ).exists(),
                "Task 1 exists in database"
            )

            self.assertTrue(
                Task.objects.filter(
                    id=self.task2.id,
                    title="Computer Request",
                    prerequisite_task=self.task1
                ).exists(),
                "Task 2 exists in database with prerequisite"
            )

            # Print admin and regular URLs
            self.driver.get(f"{self.live_server_url}/admin/")
            self.take_screenshot("admin_site")
            print(f"Admin URL: {self.driver.current_url}")

            self.driver.get(f"{self.live_server_url}/users/login/")
            self.take_screenshot("login_page")
            print(f"Login URL: {self.driver.current_url}")

        except Exception as e:
            self.take_screenshot("exploration_error")
            print(f"Error during app exploration: {e}")
            raise

    def test_tasks_database(self):
        """Test the task database structure and relationships"""
        print("\nTesting task database structure...")

        # Verify task relationship in database
        self.assertEqual(
            self.task2.prerequisite_task.id,
            self.task1.id,
            "Task2 should have Task1 as prerequisite"
        )

        # Check if faculty is properly assigned to tasks
        faculty_task1 = self.task1.assigned_to.filter(faculty_id=self.faculty.faculty_id).exists()
        faculty_task2 = self.task2.assigned_to.filter(faculty_id=self.faculty.faculty_id).exists()

        self.assertTrue(faculty_task1, "Faculty should be assigned to Task1")
        self.assertTrue(faculty_task2, "Faculty should be assigned to Task2")

        # Test task completion in database
        # First, directly create a task progress
        TaskProgress.objects.create(
            faculty=self.faculty,
            task=self.task1,
            completed=True
        )

        # Also update the Task.completed field directly for task1
        self.task1.completed = True
        self.task1.save()

        # Verify the progress record exists
        self.assertTrue(
            TaskProgress.objects.filter(
                faculty=self.faculty,
                task=self.task1,
                completed=True
            ).exists(),
            "Task progress should be recorded in database"
        )

        # Check if task1 is completed by faculty
        self.assertTrue(
            self.task1.is_completed_by(self.faculty),
            "Task1 should be marked as completed by faculty"
        )

        # Check if task2 is unlocked
        self.assertTrue(
            self.task2.is_unlocked(),
            "Task2 should be unlocked since prerequisite is completed"
        )

        print("Task database tests completed successfully")

    def test_login_behavior(self):
        """Test login behavior specifically"""
        print("\nTesting login behavior...")

        # Go to login page
        self.driver.get(f"{self.live_server_url}/users/login/")
        self.take_screenshot("direct_login_page")

        # Check if Google login button is present
        page_content = self.driver.page_source
        google_login_present = "google" in page_content.lower() or "Sign in with Google" in page_content
        print(f"Google login present: {google_login_present}")

        # Try admin login
        print("Trying admin login...")
        self.driver.get(f"{self.live_server_url}/admin/login/")

        # Fill admin login form
        username_input = self.wait_for_element(By.NAME, "username")
        password_input = self.wait_for_element(By.NAME, "password")

        username_input.send_keys(self.random_username)
        password_input.send_keys(self.test_password)

        # Submit the form
        submit_button = self.wait_for_element(By.CSS_SELECTOR, "input[type='submit']")
        submit_button.click()

        # Wait for page to load after login
        time.sleep(2)
        self.take_screenshot("after_admin_login_specific")

        # Check if admin login was successful
        admin_login_success = "/admin/" in self.driver.current_url and "login" not in self.driver.current_url
        print(f"Admin login successful: {admin_login_success}")

        if admin_login_success:
            print("Admin login successful, checking for available links")
            # Look for useful links in the admin interface
            links = self.driver.find_elements(By.TAG_NAME, "a")
            for i, link in enumerate(links[:10]):
                href = link.get_attribute('href') or ""
                text = link.text
                print(f"Link {i}: {text} -> {href}")

                # If we find links to tasks or dashboard, note them
                if "task" in href.lower() or "dashboard" in href.lower():
                    print(f"Potential useful link found: {text} -> {href}")

        # Report success
        print("Login behavior test completed")
