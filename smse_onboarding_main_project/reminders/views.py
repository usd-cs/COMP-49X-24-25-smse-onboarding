from django.shortcuts import redirect
from users.models import Faculty
from tasks.models import Task
from django.core.mail import send_mail
from django.conf import settings
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

def send_reminder(request, faculty_id, current_task_id):
    if request.method == 'POST':
        faculty = Faculty.objects.get(faculty_id=faculty_id)
        current_task = Task.objects.get(id=current_task_id)

        if current_task.remaining_days > 1:
            days_remaining = f"You have {current_task.remaining_days} days remaining to complete this task."
            time_remaining = f"{current_task.remaining_days} days"
        elif current_task.remaining_days <= 1 and current_task.remaining_days > 0:
            days_remaining = "You have less than 24 hours remaining to complete this task."
            time_remaining = "Less than 24 hours"
        else:
            days_remaining = "This task is overdue."
            time_remaining = "Overdue"

        first_sentence = f"This is a reminder about your new hire onboarding task: {current_task.title}."
        second_sentence = f"This task is due on {current_task.deadline.strftime('%B %d, %Y, %I:%M %p')}."
        third_sentence = f"{days_remaining}"
        fourth_sentence = "Please complete this task as soon as possible."
        fifth_sentence = "Please log in to the SMSE Onboarding Portal at https://smse-onboarding.dedyn.io to view the task and complete it."

        message = f"""Hello {faculty.first_name} {faculty.last_name},

{first_sentence} {second_sentence} {third_sentence} {fourth_sentence} {fifth_sentence}

See below for the task details:

Title: {current_task.title}
Created: {current_task.created_at.strftime('%B %d, %Y, %I:%M %p')}
Deadline: {current_task.deadline.strftime('%B %d, %Y, %I:%M %p')}
Prerequisite Task: {current_task.prerequisite_task.title if current_task.prerequisite_task else "None"}
Remaining Time: {time_remaining}
Description: {current_task.description}

If you have any questions, please contact the SMSE Admin team at smseadmin@sandiego.edu.

Thank you,

SMSE Admin Team
        """
        
        # Create a custom SSL context that allows unverified certificates
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Create message
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = faculty.email
        msg['Subject'] = f"Reminder for New Hire Onboarding Task: {current_task.title}"
        msg.attach(MIMEText(message, 'plain'))

        # Send email using SMTP with custom SSL context
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls(context=context)
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.send_message(msg)

    return redirect('dashboard:admin_home')