from django.urls import path
from . import views
from django.shortcuts import redirect

app_name = 'dashboard'

# Helper function to route users based on their role
def dashboard_router(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('dashboard:admin_home')
    return redirect('dashboard:new_hire_home')

urlpatterns = [
    path('', dashboard_router, name='dashboard_router'),
    path('newhire/', views.new_hire_home, name='new_hire_home'),
    path('admin/', views.admin_home, name='admin_home'),
    path('faculty-directory/', views.faculty_directory, name='faculty_directory'),
    path('complete-task/<int:task_id>/', views.complete_task, name='complete_task'),
    path('continue-task/<int:task_id>/', views.continue_task, name='continue_task'),
]

