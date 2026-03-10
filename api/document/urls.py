from django.urls import path
from api.document.document_views import DocumentListCreateView, DocumentRetrieveUpdateDeleteView, DocumentInsightView


urlpatterns = [
    path('document/', DocumentListCreateView.as_view(), name="document_list_create"),
    path('insight/', DocumentInsightView.as_view(), name="document_insight"),
    path('document/<uuid:pk>/', DocumentRetrieveUpdateDeleteView.as_view(), name="document_retrieve_update_delete"),
]
