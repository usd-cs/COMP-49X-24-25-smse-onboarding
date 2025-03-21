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
    path('home/', include('tasks.urls', namespace='tasks')),  # Keep old tasks URLs
    path('documents/', include('documents.urls', namespace='documents')),
    path('users/', include('users.urls', namespace='users')),
    path('admin-dashboard/', admin_home, name='admin_dashboard'),  # Add this back
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),  # New dashboard URLs
    path('logout/', auth_views.LogoutView.as_view(next_page='users:login'), name='logout'),
    path('social-auth/', include('social_django.urls', namespace='social')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
