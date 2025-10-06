from rest_framework import serializers
from .models import SensorDevice, SensorReading

class SensorDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorDevice
        fields = '__all__'

class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = '__all__'

class SensorReadingCreateSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = SensorReading
        fields = ['device_id', 'flow_rate', 'pressure', 'temperature', 'battery_level']
    
    def create(self, validated_data):
        device_id = validated_data.pop('device_id')
        sensor = SensorDevice.objects.get(device_id=device_id)
        return SensorReading.objects.create(sensor=sensor, **validated_data)