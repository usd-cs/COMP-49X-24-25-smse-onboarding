"""
URL configuration for smse_onboarding project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from tasks.views import custom_login
from dashboard.views import admin_home  # changed admin view name

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='dashboard/', permanent=True)),
    path('home/', include('tasks.urls', namespace='tasks')),  # Old tasks URLs
    path('documents/', include('documents.urls', namespace='documents')),  # Document management
    path('users/', include('users.urls', namespace='users')),  # User management
    path('admin-dashboard/', admin_home, name='admin_dashboard'),  # Custom admin dashboard
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),  # New dashboard
    path('logout/', auth_views.LogoutView.as_view(next_page='users:login'), name='logout'),  # Global logout
    path('social-auth/', include('social_django.urls', namespace='social')),  # Social authentication
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',  # Move this before get_username
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)
