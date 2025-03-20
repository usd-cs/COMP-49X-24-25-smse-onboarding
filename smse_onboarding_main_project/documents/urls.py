from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.show_documents, name='list'),
    path('upload/', views.upload_document, name='upload'),
    path('download/<int:doc_id>/', views.download_document, name='download'),
    path('delete/<int:doc_id>/', views.delete_document, name='delete'),
]
