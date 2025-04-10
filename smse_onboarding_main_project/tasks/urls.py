from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.home, name="home"),
    path('complete-task/<int:task_id>/', views.complete_task, name='complete_task'),
    path('continue-task/<int:task_id>/', views.continue_task, name='continue_task'),
    path('help-guide/', views.help_guide, name="help_guide"),
]
