from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'sensors', api_views.SensorDeviceViewSet)
router.register(r'readings', api_views.SensorReadingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]