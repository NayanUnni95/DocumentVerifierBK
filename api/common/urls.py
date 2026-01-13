from django.urls import path
from api.common.common_views import Common

urlpatterns = [
    path('health/', Common.as_view(), name="health_check"),
]
