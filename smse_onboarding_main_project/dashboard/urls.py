from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.new_hire_home, name='new_hire_home'),
    path('admin/', views.admin_home, name='admin_home'),
    path('complete-task/<int:task_id>/', views.complete_task, name='complete_task'),
    path('continue-task/<int:task_id>/', views.continue_task, name='continue_task'),
]

