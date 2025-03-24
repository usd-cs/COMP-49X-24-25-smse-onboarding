from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.show_documents, name='show_documents'),
    path('faculty/<int:faculty_id>/', views.show_documents, name='faculty_documents'),
    path('upload/', views.upload_document, name='upload_document'),
    path('delete/<int:doc_id>/', views.delete_document, name='delete_document'),
    path('download/<int:doc_id>/', views.download_document, name='download_document'),
]
