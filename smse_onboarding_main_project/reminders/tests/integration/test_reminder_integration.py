from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Faculty
from tasks.models import Task
from reminders.models import Reminder
from reminders.views import notifications_page, send_notification_faculty, send_notification_admin
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import datetime, timedelta

class ReminderIntegrationTests(TestCase):
    """Integration tests for reminder functionality"""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests in this class."""

        User.objects.all().delete()
        # Create test faculty
        cls.user1 = User.objects.create_user(
            pk=1,
            username='longpham',
            password='password123',
            email='longpham@sandiego.edu',
            is_active=True
        )
        # Create test admin
        cls.user2 = User.objects.create_user(
            pk=2,
            username='sbello',
            password='password123',
            email='sbello@sandiego.edu',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )

        Faculty.objects.all().delete()
        # Create test faculty
        cls.faculty1 = Faculty.objects.create(
            user=cls.user1,
            faculty_id=1,
            first_name='Long',
            last_name='Pham',
            job_role='Professor',
            engineering_dept='Computer Science',
            email='longpham@sandiego.edu',
            phone='1234567890',
            zoom_phone='0987654321',
            office_room='CS101',
            hire_date='2024-01-15T08:00:00-08:00',
            mailing_list_status=False,
            bio='Test bio',
            completed_onboarding=False
        )
        cls.faculty2 = Faculty.objects.create(
            user=cls.user2,
            faculty_id=2,
            first_name='Shayna',
            last_name='Bello',
            job_role='Assistant Professor',
            engineering_dept='Electrical Engineering',
            email='sbello@sandiego.edu',
            phone='987654321',
            zoom_phone='0123456789',
            office_room='EE102',
            hire_date='2024-02-01T08:00:00-08:00',
            mailing_list_status=True,
            bio='Another test bio',
            completed_onboarding=False
        )

        Task.objects.all().delete()
        # Create tasks
        cls.task1 = Task.objects.create(
            title='Task 1',
            description='Description 1',
            completed=False,
            deadline=parse_datetime('2024-11-06T09:30:00-08:00')
        )
        cls.task1.created_at = datetime(2024, 11, 5, 9, 30, 0, tzinfo=timezone.get_default_timezone())
        cls.task1.save(update_fields=['created_at'])
        cls.task2 = Task.objects.create(
            title='Task 2',
            description='Description 2',
            completed=False,
            deadline=parse_datetime('2024-11-07T09:30:00-08:00')
        )
        cls.task2.created_at = datetime(2024, 11, 5, 9, 30, 0, tzinfo=timezone.get_default_timezone())
        cls.task2.save(update_fields=['created_at'])
        cls.task3 = Task.objects.create(
            title='Task 3',
            description='Description 3',
            completed=False,
            deadline=parse_datetime('2024-11-08T09:30:00-08:00')
        )
        cls.task3.created_at = datetime(2024, 11, 5, 9, 30, 0, tzinfo=timezone.get_default_timezone())
        cls.task3.save(update_fields=['created_at'])

        Reminder.objects.all().delete()
        # Create reminders
        cls.reminder1 = Reminder.objects.create(
            faculty=cls.faculty1,
            task=cls.task1,
            reminder_date=parse_datetime('2024-11-05T09:30:00-08:00'),
            is_read=False,
            title='Reminder for New Hire Onboarding Task: Task 1',
            message='This is a reminder'
        )
        cls.reminder2 = Reminder.objects.create(
            faculty=cls.faculty1,
            task=cls.task2,
            reminder_date=parse_datetime('2024-12-05T09:30:00-08:00'),
            is_read=False,
            title='Reminder for New Hire Onboarding Task: Task 2',
            message='This is another reminder'
        )

    def setUp(self):
        """Set up for each test."""
        self.client = Client()

    def test_notifications_page_flow(self):
        """Test that the notifications page can be shown successfully"""
        self.client.login(username='longpham', password='password123')
        request = self.client.get(reverse('reminders:notifications'), follow=True).wsgi_request
        request.user = self.user1

        # Call the view function directly
        response = notifications_page(request)

        # Check the final response after following redirects
        self.assertEqual(response.status_code, 200)

        self.assertIn(str(self.reminder1.title).encode(), response.content)
        self.assertIn(str(self.reminder2.title).encode(), response.content)

        title1_pos = response.content.find(self.reminder1.title.encode())
        title2_pos = response.content.find(self.reminder2.title.encode())

        self.assertGreater(title1_pos, title2_pos,
                           f"{self.reminder2.title} should appear before {self.reminder1.title} in the response content")        

    def test_send_notification_faculty_flow(self):
        """Test that the faculty notification is sent successfully"""
        send_notification_faculty(self.faculty1, self.task3, "You have 1 day remaining.", "1 day")

        sent_notification = Reminder.objects.get(faculty=self.faculty1, task=self.task3)

        first_sentence = "This is a reminder about your new hire onboarding task: Task 3."
        second_sentence = "This task is due on November 08, 2024, 09:30 AM."
        third_sentence = "You have 1 day remaining."
        fourth_sentence = "Please complete this task as soon as possible."
        fifth_sentence = "Please navigate to the new hire dashboard in the SMSE Onboarding Portal to view the task and complete it."

        message = f"""Hello Long Pham,

{first_sentence} {second_sentence} {third_sentence} {fourth_sentence} {fifth_sentence}

See below for the task details:

Title: Task 3
Created: November 05, 2024, 09:30 AM
Deadline: November 08, 2024, 09:30 AM
Prerequisite Task: None
Remaining Time: 1 day
Description: Description 3

If you have any questions, please contact the SMSE Admin team at smseadmin@sandiego.edu.

Thank you,

SMSE Admin Team"""

        self.assertEqual(sent_notification.faculty, self.faculty1)
        self.assertEqual(sent_notification.task, self.task3)
        self.assertEqual(sent_notification.is_read, False)
        self.assertEqual(sent_notification.title, "Reminder for New Hire Onboarding Task: Task 3")
        self.assertEqual(sent_notification.message, message)

    def test_send_notification_admin_flow(self):
        """Test that the admin notification is sent successfully"""
        send_notification_admin(self.faculty2, self.faculty1, self.task3, "This user has less than 24 hours remaining.")

        sent_notification = Reminder.objects.get(faculty=self.faculty2, secondary_faculty=self.faculty1, task=self.task3)

        first_sentence = "This is a reminder about Long Pham's onboarding task: Task 3."
        second_sentence = "This task is due on November 08, 2024, 09:30 AM."
        third_sentence = "This user has less than 24 hours remaining."
        fourth_sentence = "Please have them complete this task as soon as possible."
        fifth_sentence = "Please have them navigate to the new hire dashboard in the SMSE Onboarding Portal to view the task and complete it."

        message = f"""Hello Shayna Bello,

{first_sentence} {second_sentence} {third_sentence} {fourth_sentence} {fifth_sentence}

See below for the task details:

Title: Task 3
Assigned To: Long Pham
Created: November 05, 2024, 09:30 AM
Deadline: November 08, 2024, 09:30 AM
Prerequisite Task: None
Remaining Time: Less than 24 hours
Description: Description 3"""

        self.assertEqual(sent_notification.faculty, self.faculty2)
        self.assertEqual(sent_notification.secondary_faculty, self.faculty1)
        self.assertEqual(sent_notification.task, self.task3)
        self.assertEqual(sent_notification.is_read, False)
        self.assertEqual(sent_notification.title, "Reminder for Long Pham's Onboarding Task: Task 3")
        self.assertEqual(sent_notification.message, message)