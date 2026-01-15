from django.urls import path

from api.auth.auth_views import RegisterView, LoginView


urlpatterns = [
    path('register/', RegisterView.as_view(), name="register_user"),
    path('login/', LoginView.as_view(), name="login_user"),
]
