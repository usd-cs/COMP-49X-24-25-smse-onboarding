from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='users:login'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('dismiss-welcome/', views.dismiss_welcome_banner, name='dismiss_welcome'),
    path('show-welcome/', views.show_welcome, name='show_welcome'),
    path('welcome-info/', views.welcome_info, name='welcome_info'),
    path('admin-help-guide/', views.admin_help_guide, name='admin_help_guide'),
    path('update-profile/', views.update_profile, name='update_profile'),
]
