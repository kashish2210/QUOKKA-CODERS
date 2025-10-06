from django.urls import path
from . import views

app_name = 'sensors'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('sensors/', views.sensor_list, name='sensor_list'),
    path('sensors/<str:device_id>/', views.sensor_detail, name='sensor_detail'),
    path('zones/', views.zones_list, name='zones_list'),
]