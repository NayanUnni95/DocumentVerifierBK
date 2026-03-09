from django.urls import path
from api.document.document_views import DocumentListCreateView, DocumentRetrieveUpdateDeleteView


urlpatterns = [
    path('document/', DocumentListCreateView.as_view(), name="document_list_create"),
    path('document/<uuid:pk>/', DocumentRetrieveUpdateDeleteView.as_view(), name="document_retrieve_update_delete"),
]
