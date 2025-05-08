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
    path('update-settings/', views.update_settings, name='update_settings'),
    path('api/faculty/<int:faculty_id>/tasks/', views.faculty_tasks, name='faculty_tasks'),
    path('api/faculty/<int:faculty_id>/', views.get_faculty, name='get_faculty'),
    path('api/faculty/<int:faculty_id>/update/', views.update_faculty, name='update_faculty'),
    path('api/new-hire-deadlines/', views.get_new_hire_deadlines, name='get_new_hire_deadlines'),
    
    # New endpoints for user permissions management
    path('api/faculty/<int:faculty_id>/user-permissions/', views.get_user_permissions, name='get_user_permissions'),
    path('api/faculty/user-permissions/<int:user_id>/update/', views.update_user_permissions, name='update_user_permissions'),
    path('task-management/', views.task_management, name='task_management'),
    path('edit-task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('api/edit-task/<int:task_id>/', views.api_edit_task, name='api_edit_task'),
    path('api/add-task/', views.api_add_task, name='api_add_task'),
    path('api/delete-task/<int:task_id>/', views.api_delete_task, name='api_delete_task'),
]

