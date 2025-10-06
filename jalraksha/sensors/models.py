from django.db import models
from django.contrib.auth.models import User

class SensorDevice(models.Model):
    SENSOR_TYPES = [
        ('FLOW', 'Ultrasonic Flow Sensor'),
        ('PRESSURE', 'Pressure Sensor'),
    ]
    DEPLOYMENT_TYPES = [
        ('MUNICIPAL', 'Municipal Distribution'),
        ('RESIDENTIAL', 'Residential Society'),
    ]
    
    device_id = models.CharField(max_length=50, unique=True)
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPES)
    deployment_type = models.CharField(max_length=20, choices=DEPLOYMENT_TYPES)
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    installation_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    last_maintenance = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.device_id} - {self.location}"

class SensorReading(models.Model):
    sensor = models.ForeignKey(SensorDevice, on_delete=models.CASCADE, related_name='readings')
    timestamp = models.DateTimeField(auto_now_add=True)
    flow_rate = models.FloatField(null=True, blank=True, help_text='Liters per minute')
    pressure = models.FloatField(null=True, blank=True, help_text='PSI')
    temperature = models.FloatField(null=True, blank=True, help_text='Celsius')
    battery_level = models.IntegerField(default=100, help_text='Percentage')
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sensor', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.sensor.device_id} - {self.timestamp}"

class WaterConsumptionZone(models.Model):
    name = models.CharField(max_length=100)
    zone_type = models.CharField(max_length=50)
    contact_person = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    sensors = models.ManyToManyField(SensorDevice, related_name='zones')
    
    def __str__(self):
        return self.name