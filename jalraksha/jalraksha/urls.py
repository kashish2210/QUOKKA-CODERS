from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sensors.urls')),
    path('analytics/', include('analytics.urls')),
    path('alerts/', include('alerts.urls')),
    path('api/', include('sensors.api_urls')),
]