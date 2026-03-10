from django.urls import path
from api.document.document_views import DocumentVerifyView, DocumentPublicView

urlpatterns = [
    path('document/', DocumentVerifyView.as_view(), name='document_verify'),
    path('view-document/<uuid:pk>/', DocumentPublicView.as_view(), name='document_public_view'),
]
