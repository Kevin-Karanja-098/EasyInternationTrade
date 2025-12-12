# accounts/urls.py
from django.urls import path
from .views import RegisterView, UserDetailView
from .views_documents import DocumentUploadView, DocumentListView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="account-register"),
    path("me/", UserDetailView.as_view(), name="account-me"),
    path("documents/upload/", DocumentUploadView.as_view(), name="document-upload"),
    path("documents/", DocumentListView.as_view(), name="document-list"),
]
