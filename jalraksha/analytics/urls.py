from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('leaks/', views.leak_list, name='leak_list'),
    path('consumption/', views.consumption_patterns, name='consumption_patterns'),
]