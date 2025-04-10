from selenium.webdriver.common.by import By
from .base_test import BaseE2ETest

class LoginTest(BaseE2ETest):
    """End-to-end tests for login functionality"""

    def test_login_page_loads(self):
        """Test that the login page loads correctly.."""
        print("\nTesting login page load...")

        # Navigate to login page
        self.driver.get(f"{self.live_server_url}/users/login/")
        print(f"Navigated to: {self.driver.current_url}")

        # Take screenshot of initial page load
        screenshot_path = self.take_screenshot("login_page_initial")
        print(f"Screenshot saved to: {screenshot_path}")

        # Check for key elements
        print("Checking for key elements...")
        self.wait_for_element(By.CLASS_NAME, "login-card")
        self.wait_for_element(By.CLASS_NAME, "portal-title")
        self.wait_for_element(By.CLASS_NAME, "google-btn")
        print("All key elements found!")

        # Verify the page title
        print(f"Page title: {self.driver.title}")
        self.assertIn("SMSE Onboarding | Login", self.driver.title)

        # Verify the portal title text
        portal_title = self.driver.find_element(By.CLASS_NAME, "portal-title")
        print(f"Portal title text: {portal_title.text}")
        self.assertIn("SMSE", portal_title.text)
        self.assertIn("ONBOARDING PORTAL", portal_title.text)

    def test_google_login_button(self):
        """Test that the Google login button is present and clickable"""
        print("\nTesting Google login button...")

        # Navigate to login page
        self.driver.get(f"{self.live_server_url}/users/login/")
        print(f"Navigated to: {self.driver.current_url}")

        # Find and verify Google login button
        google_btn = self.wait_for_element_clickable(By.CLASS_NAME, "google-btn")
        print(f"Google button text: {google_btn.text}")
        self.assertIn("Log in with Google", google_btn.text)

        # Verify the button contains the Google icon
        google_icon = google_btn.find_element(By.CLASS_NAME, "google-icon")
        print("Google icon found and displayed")
        self.assertTrue(google_icon.is_displayed())

        # Take screenshot of the Google button
        screenshot_path = self.take_screenshot("google_login_button")
        print(f"Screenshot saved to: {screenshot_path}")

        # Verify the button is clickable
        print("Verifying button is clickable...")
        self.assertTrue(google_btn.is_enabled())
        print("Button is clickable!")

    def test_login_redirects(self):
        """Test that unauthenticated users are redirected to login"""
        print("\nTesting login redirects...")

        # Try to access a protected page
        self.driver.get(f"{self.live_server_url}/dashboard/")
        print(f"Attempted to access: {self.driver.current_url}")

        # Take screenshot of redirect
        screenshot_path = self.take_screenshot("login_redirect")
        print(f"Screenshot saved to: {screenshot_path}")

        # Verify we're redirected to login page
        print("Verifying redirect to login page...")
        self.assertIn("/users/login/", self.driver.current_url)
        print(f"Successfully redirected to: {self.driver.current_url}")

        # Verify the login page elements are present
        print("Verifying login page elements...")
        self.wait_for_element(By.CLASS_NAME, "login-card")
        self.wait_for_element(By.CLASS_NAME, "google-btn")
        print("All login page elements present!")
