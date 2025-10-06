from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    path('', views.alerts_list, name='alerts_list'),
    path('<int:alert_id>/', views.alert_detail, name='alert_detail'),
    path('<int:alert_id>/resolve/', views.mark_resolved, name='mark_resolved'),
]