from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from sensors import views as sensor_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('terminal/execute/', sensor_views.execute_command, name='terminal_execute'),
    path('terminal/output/', sensor_views.get_output, name='terminal_output'),
    path('', include('sensors.urls')),
    path('analytics/', include('analytics.urls')),
    path('alerts/', include('alerts.urls')),
    path('api/', include('sensors.api_urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)