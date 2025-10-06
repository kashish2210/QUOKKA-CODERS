from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Avg, Max, Min, Count
from django.utils import timezone
from datetime import timedelta
from .models import SensorDevice, SensorReading, WaterConsumptionZone

def dashboard(request):
    total_sensors = SensorDevice.objects.count()
    active_sensors = SensorDevice.objects.filter(is_active=True).count()
    
    # Recent readings
    recent_readings = SensorReading.objects.select_related('sensor').all()[:10]
    
    # Get all sensors with latest reading
    sensors = SensorDevice.objects.all()
    
    context = {
        'total_sensors': total_sensors,
        'active_sensors': active_sensors,
        'recent_readings': recent_readings,
        'sensors': sensors,
    }
    return render(request, 'sensors/dashboard.html', context)

def sensor_list(request):
    sensors = SensorDevice.objects.all()
    context = {'sensors': sensors}
    return render(request, 'sensors/sensor_list.html', context)

def sensor_detail(request, device_id):
    sensor = get_object_or_404(SensorDevice, device_id=device_id)
    
    # Get readings from last 24 hours
    since = timezone.now() - timedelta(hours=24)
    readings = sensor.readings.filter(timestamp__gte=since)
    
    # Statistics
    stats = readings.aggregate(
        avg_flow=Avg('flow_rate'),
        max_flow=Max('flow_rate'),
        min_flow=Min('flow_rate'),
        avg_pressure=Avg('pressure'),
        total_readings=Count('id')
    )
    
    context = {
        'sensor': sensor,
        'readings': readings[:50],
        'stats': stats,
    }
    return render(request, 'sensors/sensor_detail.html', context)

def zones_list(request):
    zones = WaterConsumptionZone.objects.all()
    context = {'zones': zones}
    return render(request, 'sensors/zones_list.html', context)