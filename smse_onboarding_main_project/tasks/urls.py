from django.urls import path

from . import views

app_name = "tasks"


urlpatterns = [
    path("", views.home, name="home"),
    path('complete-task/<int:task_id>/', views.complete_task, name='complete_task'),
    path('continue-task/<int:task_id>/', views.continue_task, name='continue_task'),
    path('admin-help/', views.admin_help, name="admin_help"),
    path('documents/', views.show_documents, name='document_list'),
    path('documents/faculty/<int:faculty_id>/', views.show_documents, name='faculty_documents'),
    path('documents/upload/', views.upload_document, name='upload_document'),
    path('documents/delete/<int:doc_id>/', views.delete_document, name='delete_document'),
]
