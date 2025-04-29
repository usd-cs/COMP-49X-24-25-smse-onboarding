from django.shortcuts import redirect, get_object_or_404
from users.models import Faculty
from tasks.models import Task
from reminders.models import Reminder
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from dashboard.views import is_admin, get_faculty_from_request
from django.core.exceptions import PermissionDenied

@login_required
def notifications_page(request):
    """Render the notifications page"""
    user = request.user

    # Check if user is staff or admin, redirect to admin dashboard if so
    if user.is_staff or is_admin(user):
        return redirect('dashboard:admin_home')
    
    faculty = get_faculty_from_request(request)
    if not faculty:
        if request.user.is_superuser:
            return redirect('dashboard:admin_home')
        return redirect('users:login')
    
    if not user.is_staff and (not hasattr(user, 'faculty_profile') or user.faculty_profile.faculty_id != faculty.faculty_id):
        raise PermissionDenied
    
    reminders = Reminder.objects.filter(faculty=faculty)

    # Render the notifications page for the specific faculty member
    return render(request, 'reminders/notifications.html', {
        'reminders': reminders,
        'faculty': faculty,
    })

@login_required
def mark_as_read(request, reminder_id):
    reminder = get_object_or_404(Reminder, reminder_id=reminder_id)
    reminder.mark_as_read()
    return redirect('reminders:notifications')

@login_required
def mark_as_unread(request, reminder_id):
    reminder = get_object_or_404(Reminder, reminder_id=reminder_id)
    reminder.mark_as_unread()
    return redirect('reminders:notifications')

@login_required
def send_reminder(request, faculty_id, current_task_id):
    if request.method == 'POST':
        faculty = Faculty.objects.get(faculty_id=faculty_id)
        current_task = Task.objects.get(id=current_task_id)

        if current_task.remaining_days > 1:
            days_remaining = f"You have {current_task.remaining_days} days remaining to complete this task."
            time_remaining = f"{current_task.remaining_days} days"
        elif (current_task.deadline - timezone.now()).total_seconds() / 3600 <= 24 and (current_task.deadline - timezone.now()).total_seconds() / 3600 > 0:
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

SMSE Admin Team"""
        
        send_mail(
            f"Reminder for New Hire Onboarding Task: {current_task.title}",
            message,
            settings.EMAIL_HOST_USER,
            [faculty.email],
            fail_silently=False,
        )

        send_notification(faculty, current_task, days_remaining, time_remaining)

    return redirect('dashboard:admin_home')

def send_notification(faculty, current_task, days_remaining, time_remaining):
    first_sentence = f"This is a reminder about your new hire onboarding task: {current_task.title}."
    second_sentence = f"This task is due on {current_task.deadline.strftime('%B %d, %Y, %I:%M %p')}."
    third_sentence = f"{days_remaining}"
    fourth_sentence = "Please complete this task as soon as possible."
    fifth_sentence = "Please navigate to the new hire dashboard in the SMSE Onboarding Portal to view the task and complete it."

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

SMSE Admin Team"""
    
    notification = Reminder(
        faculty=faculty,
        task=current_task,
        reminder_date=timezone.now(),
        is_read=False,
        title=f"Reminder for New Hire Onboarding Task: {current_task.title}",
        message=message,
    )
    notification.save()
