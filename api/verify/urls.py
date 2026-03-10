from django.urls import path
from api.document.document_views import DocumentVerifyView

urlpatterns = [
    path('document/', DocumentVerifyView.as_view(), name='document_verify'),
]
