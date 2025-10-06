import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import timedelta
from django.utils import timezone

class LeakDetectionAI:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.is_trained = False
    
    def train(self, sensor_id):
        """Train on historical data for a specific sensor"""
        from sensors.models import SensorReading, SensorDevice
        
        sensor = SensorDevice.objects.get(id=sensor_id)
        readings = sensor.readings.filter(
            timestamp__gte=timezone.now() - timedelta(days=30)
        ).values_list('flow_rate', 'pressure')
        
        if len(readings) < 100:
            return False
        
        X = np.array(readings)
        self.model.fit(X)
        self.is_trained = True
        return True
    
    def detect_anomaly(self, flow_rate, pressure):
        """Detect if current reading is anomalous"""
        if not self.is_trained:
            return False, 0.0
        
        X = np.array([[flow_rate, pressure]])
        prediction = self.model.predict(X)
        score = self.model.score_samples(X)[0]
        
        is_anomaly = prediction[0] == -1
        confidence = abs(score)
        
        return is_anomaly, confidence
    
    def detect_continuous_flow(self, sensor_id, hours=24):
        """Detect continuous flow (potential leak)"""
        from sensors.models import SensorReading, SensorDevice
        
        sensor = SensorDevice.objects.get(id=sensor_id)
        since = timezone.now() - timedelta(hours=hours)
        readings = sensor.readings.filter(timestamp__gte=since).order_by('timestamp')
        
        if readings.count() < 20:
            return False, 0
        
        flow_rates = [r.flow_rate for r in readings if r.flow_rate]
        if not flow_rates:
            return False, 0
        
        # Check for continuous non-zero flow
        avg_flow = np.mean(flow_rates)
        std_flow = np.std(flow_rates)
        
        # Low variance + non-zero flow = potential leak
        if avg_flow > 0.5 and std_flow < (avg_flow * 0.2):
            estimated_loss = avg_flow * 60  # Convert to liters per hour
            return True, estimated_loss
        
        return False, 0