from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('common/', include('api.common.urls')),
    path('auth/', include('api.auth.urls')),
    path('doc/', include('api.document.urls')),
    path('verify/', include('api.verify.urls')),
    path('user/', include('api.user.urls')),
]