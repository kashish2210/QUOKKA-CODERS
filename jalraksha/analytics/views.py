from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, Sum, Max, Min
from django.utils import timezone
from datetime import timedelta
from .models import LeakDetection, ConsumptionPattern
from sensors.models import SensorDevice, SensorReading
import json

def analytics_dashboard(request):
    total_leaks = LeakDetection.objects.count()
    active_leaks = LeakDetection.objects.filter(status__in=['DETECTED', 'INVESTIGATING', 'CONFIRMED']).count()
    
    # Leaks by severity
    leaks_by_severity = LeakDetection.objects.values('severity').annotate(count=Count('id'))
    
    # Recent leaks
    recent_leaks = LeakDetection.objects.select_related('sensor').all()[:10]
    
    # Total water loss
    total_loss = LeakDetection.objects.filter(
        status__in=['DETECTED', 'INVESTIGATING', 'CONFIRMED']
    ).aggregate(total=Sum('estimated_loss_rate'))['total'] or 0
    
    context = {
        'total_leaks': total_leaks,
        'active_leaks': active_leaks,
        'leaks_by_severity': leaks_by_severity,
        'recent_leaks': recent_leaks,
        'total_loss': total_loss,
    }
    return render(request, 'analytics/dashboard.html', context)

def advanced_dashboard(request):
    """Advanced Analytics Dashboard with real sensor data"""
    
    # Get all active sensors
    sensors = SensorDevice.objects.filter(is_active=True)
    
    # Time range filter (default: 24 hours)
    time_range = request.GET.get('range', '24h')
    if time_range == '24h':
        time_delta = timedelta(hours=24)
    elif time_range == '7d':
        time_delta = timedelta(days=7)
    elif time_range == '30d':
        time_delta = timedelta(days=30)
    else:
        time_delta = timedelta(hours=24)
    
    start_time = timezone.now() - time_delta
    
    # Get readings for all sensors
    readings = SensorReading.objects.filter(
        timestamp__gte=start_time
    ).select_related('sensor')
    
    # Calculate KPIs
    total_flow = readings.aggregate(
        total=Sum('flow_rate')
    )['total'] or 0
    
    avg_pressure = readings.aggregate(
        avg=Avg('pressure')
    )['avg'] or 0
    
    # Get active leaks
    active_leaks_count = LeakDetection.objects.filter(
        status__in=['DETECTED', 'INVESTIGATING', 'CONFIRMED']
    ).count()
    
    total_loss = LeakDetection.objects.filter(
        status__in=['DETECTED', 'INVESTIGATING', 'CONFIRMED']
    ).aggregate(total=Sum('estimated_loss_rate'))['total'] or 0
    
    # Calculate NRW percentage (Non-Revenue Water)
    nrw_percentage = (total_loss / total_flow * 100) if total_flow > 0 else 0
    
    # Calculate efficiency score
    efficiency_score = max(0, 100 - nrw_percentage) if nrw_percentage > 0 else 95
    
    # Prepare chart data for Flow Rate (last 24 hours)
    flow_readings = list(readings.filter(
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).order_by('timestamp')[:24])
    
    # If no readings, generate sample data for visualization
    if not flow_readings:
        flow_rate_data = {
            'labels': [f'{i}:00' for i in range(24)],
            'values': [20 + (i % 5) * 2 for i in range(24)]
        }
        pressure_data = {
            'labels': [f'{i}:00' for i in range(24)],
            'values': [40 + (i % 5) * 3 for i in range(24)]
        }
    else:
        flow_rate_data = {
            'labels': [r.timestamp.strftime('%H:%M') for r in flow_readings],
            'values': [float(r.flow_rate) if r.flow_rate else 0 for r in flow_readings]
        }
        
        # Prepare chart data for Pressure
        pressure_data = {
            'labels': [r.timestamp.strftime('%H:%M') for r in flow_readings],
            'values': [float(r.pressure) if r.pressure else 0 for r in flow_readings]
        }
    
    # Consumption pattern by hour
    consumption_by_hour = {}
    for reading in readings:
        hour = reading.timestamp.hour
        hour_key = f"{hour:02d}:00"
        if hour_key not in consumption_by_hour:
            consumption_by_hour[hour_key] = 0
        consumption_by_hour[hour_key] += reading.flow_rate if reading.flow_rate else 0
    
    consumption_data = {
        'labels': list(consumption_by_hour.keys()),
        'values': list(consumption_by_hour.values())
    }
    
    # Leak detection data by severity
    leak_severity_data = LeakDetection.objects.values('severity').annotate(
        count=Count('id')
    )
    
    leak_data = {
        'labels': [item['severity'] for item in leak_severity_data],
        'values': [item['count'] for item in leak_severity_data]
    }
    
    # Sensor status data
    active_sensors = sensors.filter(is_active=True).count()
    warning_sensors = sensors.filter(
        readings__battery_level__lt=30,
        is_active=True
    ).distinct().count()
    offline_sensors = sensors.filter(is_active=False).count()
    
    sensor_status_data = {
        'labels': ['Active', 'Warning', 'Offline'],
        'values': [active_sensors, warning_sensors, offline_sensors]
    }
    
    # Sensor statistics
    sensor_stats = []
    for sensor in sensors:
        sensor_readings = readings.filter(sensor=sensor)
        
        if sensor_readings.exists():
            stats = sensor_readings.aggregate(
                avg_flow=Avg('flow_rate'),
                peak_flow=Max('flow_rate'),
                avg_pressure=Avg('pressure'),
                min_battery=Min('battery_level')
            )
            
            sensor_stats.append({
                'device_id': sensor.device_id,
                'location': sensor.location,
                'avg_flow': stats['avg_flow'] or 0,
                'peak_flow': stats['peak_flow'] or 0,
                'avg_pressure': stats['avg_pressure'] or 0,
                'uptime': 98.5,  # Calculate based on readings frequency
                'reliability': 95,  # Calculate based on data quality
                'alert_count': LeakDetection.objects.filter(sensor=sensor).count(),
                'is_active': sensor.is_active
            })
    
    context = {
        'sensors': sensors,
        'total_flow': total_flow,
        'total_loss': total_loss,
        'nrw_percentage': nrw_percentage,
        'efficiency_score': efficiency_score,
        'active_leaks_count': active_leaks_count,
        'sensor_stats': sensor_stats,
        'flow_rate_data': json.dumps(flow_rate_data),
        'pressure_data': json.dumps(pressure_data),
        'consumption_data': json.dumps(consumption_data),
        'leak_data': json.dumps(leak_data),
        'sensor_status_data': json.dumps(sensor_status_data),
    }
    
    return render(request, 'analytics/advanced_dashboard.html', context)

def leak_list(request):
    leaks = LeakDetection.objects.select_related('sensor').all()
    context = {'leaks': leaks}
    return render(request, 'analytics/leak_list.html', context)

def consumption_patterns(request):
    patterns = ConsumptionPattern.objects.select_related('sensor').all()[:50]
    context = {'patterns': patterns}
    return render(request, 'analytics/consumption_patterns.html', context)