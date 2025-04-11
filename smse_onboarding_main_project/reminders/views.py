from django.shortcuts import redirect
from users.models import Faculty
from tasks.models import Task
from django.core.mail import send_mail
from django.conf import settings

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

        message = f"""Hello {faculty.first_name} {faculty.last_name},
        
This is a reminder about your new hire onboarding task: {current_task.title}. This task is due on {current_task.deadline.strftime('%B %d, %Y, %I:%M %p')}. {days_remaining} Please complete this task as soon as possible. Please log in to the SMSE Onboarding Portal at https://smse-onboarding.dedyn.io to view the task and complete it.

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
        
        send_mail(
            f"Reminder for New Hire Onboarding Task: {current_task.title}",
            message,
            settings.EMAIL_HOST_USER,
            [faculty.email],
            fail_silently=False,
        )
        
    return redirect('dashboard:admin_home')