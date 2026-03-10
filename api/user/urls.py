from django.urls import path
from api.user.user_views import UserProfileView, UserOrgView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('org/', UserOrgView.as_view(), name='user_org'),
]
