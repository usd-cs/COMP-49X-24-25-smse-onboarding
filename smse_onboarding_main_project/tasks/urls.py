from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.home, name="home"),
    path('complete-task/<int:task_id>/', views.complete_task, name='complete_task'),

    path('notifications/', views.notifications, name='notifications'),
]
