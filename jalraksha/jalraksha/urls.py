from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from sensors.views import SensorDeviceViewSet, SensorReadingViewSet

router = DefaultRouter()
router.register(r'sensors', SensorDeviceViewSet)
router.register(r'readings', SensorReadingViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]