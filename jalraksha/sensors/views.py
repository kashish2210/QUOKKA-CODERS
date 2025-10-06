from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import SensorDevice, SensorReading
from .serializers import SensorDeviceSerializer, SensorReadingSerializer, SensorReadingCreateSerializer

class SensorDeviceViewSet(viewsets.ModelViewSet):
    queryset = SensorDevice.objects.all()
    serializer_class = SensorDeviceSerializer
    
    @action(detail=True, methods=['get'])
    def recent_readings(self, request, pk=None):
        sensor = self.get_object()
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        readings = sensor.readings.filter(timestamp__gte=since)
        serializer = SensorReadingSerializer(readings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active_sensors(self, request):
        active = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)

class SensorReadingViewSet(viewsets.ModelViewSet):
    queryset = SensorReading.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SensorReadingCreateSerializer
        return SensorReadingSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Trigger anomaly detection asynchronously
        from analytics.tasks import analyze_sensor_reading
        reading_id = serializer.instance.id
        analyze_sensor_reading.delay(reading_id)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)