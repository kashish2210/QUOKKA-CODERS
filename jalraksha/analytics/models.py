from django.db import models
from sensors.models import SensorDevice

class LeakDetection(models.Model):
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('DETECTED', 'Detected'),
        ('INVESTIGATING', 'Investigating'),
        ('CONFIRMED', 'Confirmed'),
        ('REPAIRED', 'Repaired'),
        ('FALSE_ALARM', 'False Alarm'),
    ]
    
    sensor = models.ForeignKey(SensorDevice, on_delete=models.CASCADE)
    detected_at = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DETECTED')
    estimated_loss_rate = models.FloatField(help_text='Liters per hour')
    confidence_score = models.FloatField(help_text='AI confidence 0-1')
    resolved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-detected_at']
    
    def __str__(self):
        return f"Leak {self.id} - {self.sensor.location} ({self.severity})"

class ConsumptionPattern(models.Model):
    sensor = models.ForeignKey(SensorDevice, on_delete=models.CASCADE)
    date = models.DateField()
    total_consumption = models.FloatField(help_text='Liters')
    peak_hour = models.IntegerField()
    continuous_flow_detected = models.BooleanField(default=False)
    anomaly_score = models.FloatField(default=0.0)
    
    class Meta:
        unique_together = ['sensor', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.sensor.device_id} - {self.date}"