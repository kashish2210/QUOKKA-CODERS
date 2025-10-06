from celery import shared_task
from .ai_models import LeakDetectionAI
from .models import LeakDetection
from sensors.models import SensorReading
from alerts.models import Alert

@shared_task
def analyze_sensor_reading(reading_id):
    """Analyze sensor reading for anomalies"""
    reading = SensorReading.objects.get(id=reading_id)
    sensor = reading.sensor
    
    ai = LeakDetectionAI()
    
    # Train model if needed
    if not ai.is_trained:
        ai.train(sensor.id)
    
    # Check for anomaly
    is_anomaly, confidence = ai.detect_anomaly(reading.flow_rate, reading.pressure)
    
    if is_anomaly and confidence > 0.7:
        # Check for continuous flow
        has_leak, loss_rate = ai.detect_continuous_flow(sensor.id)
        
        if has_leak:
            # Determine severity
            if loss_rate > 1000:
                severity = 'CRITICAL'
                priority = 'URGENT'
            elif loss_rate > 500:
                severity = 'HIGH'
                priority = 'HIGH'
            elif loss_rate > 100:
                severity = 'MEDIUM'
                priority = 'MEDIUM'
            else:
                severity = 'LOW'
                priority = 'LOW'
            
            # Create leak detection record
            leak = LeakDetection.objects.create(
                sensor=sensor,
                severity=severity,
                estimated_loss_rate=loss_rate,
                confidence_score=confidence
            )
            
            # Create alert
            if sensor.deployment_type == 'MUNICIPAL':
                message = f"Major leak detected at {sensor.location}. Estimated loss: {loss_rate:.1f} L/hr"
            else:
                message = f"Continuous flow detected for 24 hours. Check for leaks. Estimated loss: {loss_rate:.1f} L/hr"
            
            Alert.objects.create(
                alert_type='LEAK',
                priority=priority,
                sensor=sensor,
                leak=leak,
                message=message
            )