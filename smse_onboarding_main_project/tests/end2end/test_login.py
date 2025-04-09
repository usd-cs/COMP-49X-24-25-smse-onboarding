from selenium.webdriver.common.by import By
from tests.end2end.base_test import BaseE2ETest

class LoginTest(BaseE2ETest):
    """End-to-end tests for login functionality"""

    def test_login_page_loads(self):
        """Test that the login page loads correctly"""
        # Navigate to login page
        self.driver.get(f"{self.live_server_url}/users/login/")

        # Check for key elements
        self.wait_for_element(By.CLASS_NAME, "login-card")
        self.wait_for_element(By.CLASS_NAME, "portal-title")
        self.wait_for_element(By.CLASS_NAME, "google-btn")

        # Verify the page title
        self.assertIn("SMSE Onboarding | Login", self.driver.title)

        # Verify the portal title text
        portal_title = self.driver.find_element(By.CLASS_NAME, "portal-title")
        self.assertIn("SMSE", portal_title.text)
        self.assertIn("ONBOARDING PORTAL", portal_title.text)

    def test_google_login_button(self):
        """Test that the Google login button is present and clickable"""
        # Navigate to login page
        self.driver.get(f"{self.live_server_url}/users/login/")

        # Find and verify Google login button
        google_btn = self.wait_for_element_clickable(By.CLASS_NAME, "google-btn")
        self.assertIn("Log in with Google", google_btn.text)

        # Verify the button contains the Google icon
        google_icon = google_btn.find_element(By.CLASS_NAME, "google-icon")
        self.assertTrue(google_icon.is_displayed())

        # Verify the button is clickable
        self.assertTrue(google_btn.is_enabled())

    def test_login_redirects(self):
        """Test that unauthenticated users are redirected to login"""
        # Try to access a protected page
        self.driver.get(f"{self.live_server_url}/dashboard/")

        # Verify we're redirected to login page
        self.assertIn("/users/login/", self.driver.current_url)

        # Verify the login page elements are present
        self.wait_for_element(By.CLASS_NAME, "login-card")
        self.wait_for_element(By.CLASS_NAME, "google-btn")
