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

class SensorReadingViewSet(viewsets.ModelViewSet):
    queryset = SensorReading.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SensorReadingCreateSerializer
        return SensorReadingSerializer