from django.urls import path
from . import views

app_name = 'reminders'

urlpatterns = [
    path('send-reminder/<int:faculty_id>/<int:current_task_id>/', views.send_reminder, name='send_reminder'),
    
]