from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os

class BaseE2ETest(LiveServerTestCase):
    """Base class for end-to-end tests using Selenium"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # Initialize the Chrome WebDriver
        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present and return it"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.fail(f"Element not found: {value}")

    def wait_for_element_clickable(self, by, value, timeout=10):
        """Wait for an element to be clickable and return it"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            self.fail(f"Element not clickable: {value}")

    def take_screenshot(self, name):
        """Take a screenshot and save it to the screenshots directory"""
        screenshots_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'screenshots'
        )
        os.makedirs(screenshots_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshots_dir, f"{name}.png")
        self.driver.save_screenshot(screenshot_path)
        return screenshot_path
