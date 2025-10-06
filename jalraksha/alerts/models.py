from django.db import models
from sensors.models import SensorDevice, WaterConsumptionZone
from analytics.models import LeakDetection

class Alert(models.Model):
    ALERT_TYPES = [
        ('LEAK', 'Leak Detected'),
        ('CONTINUOUS_FLOW', 'Continuous Flow'),
        ('HIGH_CONSUMPTION', 'High Consumption'),
        ('SENSOR_OFFLINE', 'Sensor Offline'),
        ('LOW_PRESSURE', 'Low Pressure'),
    ]
    PRIORITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS)
    sensor = models.ForeignKey(SensorDevice, on_delete=models.CASCADE)
    leak = models.ForeignKey(LeakDetection, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert_type} - {self.sensor.location}"