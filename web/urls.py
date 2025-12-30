from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), # Ensuring index path exists
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
]
