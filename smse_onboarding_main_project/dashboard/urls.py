from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.new_hire_home, name='new_hire_home'),
    path('admin/', views.admin_home, name='admin_home'),
]

