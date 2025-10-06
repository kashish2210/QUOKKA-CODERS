from django.urls import path
from . import views

app_name = 'sensors'

urlpatterns = [
    # Terminal as homepage
    path('terminal/', views.terminal_view, name='terminal'),
    path('terminal/execute/', views.execute_command, name='execute_command'),
    path('terminal/output/', views.get_output, name='get_output'),
    
    # Dashboard and sensor routes
    path('', views.dashboard, name='dashboard'),
    path('sensors/', views.sensor_list, name='sensor_list'),
    path('sensors/<str:device_id>/', views.sensor_detail, name='sensor_detail'),
    path('zones/', views.zones_list, name='zones_list'),
]