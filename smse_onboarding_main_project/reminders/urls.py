from django.urls import path
from . import views

app_name = 'reminders'

urlpatterns = [
    path('', views.notifications_page, name='notifications'),
    path('send-reminder-faculty/<int:faculty_id>/<int:current_task_id>/', views.send_reminder_faculty, name='send_reminder_faculty'),
    path('mark-as-read/<int:reminder_id>/', views.mark_as_read, name='mark_as_read'),
    path('mark-as-unread/<int:reminder_id>/', views.mark_as_unread, name='mark_as_unread'),
]