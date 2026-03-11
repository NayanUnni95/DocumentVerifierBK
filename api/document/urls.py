from django.urls import path
from api.document.document_views import DocumentListCreateView, DocumentRetrieveUpdateDeleteView, DocumentInsightView, ActivityListView


urlpatterns = [
    path('document/', DocumentListCreateView.as_view(), name="document_list_create"),
    path('insight/', DocumentInsightView.as_view(), name="document_insight"),
    path('activity/', ActivityListView.as_view(), name="activity_list"),
    path('document/<uuid:pk>/', DocumentRetrieveUpdateDeleteView.as_view(), name="document_retrieve_update_delete"),
]
