from django.core.management.base import BaseCommand
from django.utils import timezone
from sensors.models import SensorDevice, SensorReading
from analytics.models import LeakDetection
from alerts.models import Alert
import random
import time

class Command(BaseCommand):
    help = 'Simulate sensor data for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=5,
            help='Interval between readings in seconds'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=0,
            help='Number of readings to generate (0 for infinite)'
        )
    
    def handle(self, *args, **kwargs):
        interval = kwargs['interval']
        count = kwargs['count']
        
        sensors = SensorDevice.objects.filter(is_active=True)
        
        if not sensors.exists():
            self.stdout.write(self.style.ERROR('No active sensors found. Please create sensors first.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Starting simulation for {sensors.count()} sensors'))
        
        readings_generated = 0
        
        try:
            while count == 0 or readings_generated < count:
                for sensor in sensors:
                    # Normal operation ranges
                    base_flow = 25.0
                    base_pressure = 45.0
                    
                    # Simulate different scenarios
                    scenario = random.random()
                    
                    if scenario < 0.7:  # Normal operation (70%)
                        flow_rate = random.uniform(base_flow - 10, base_flow + 15)
                        pressure = random.uniform(base_pressure - 10, base_pressure + 10)
                    elif scenario < 0.85:  # High consumption (15%)
                        flow_rate = random.uniform(45, 65)
                        pressure = random.uniform(40, 55)
                    elif scenario < 0.95:  # Low pressure issue (10%)
                        flow_rate = random.uniform(15, 25)
                        pressure = random.uniform(20, 30)
                    else:  # Potential leak (5%)
                        flow_rate = random.uniform(5, 15)
                        pressure = random.uniform(15, 25)
                        
                        # Create leak detection
                        if random.random() < 0.5:  # 50% chance to detect
                            leak = LeakDetection.objects.create(
                                sensor=sensor,
                                severity=random.choice(['LOW', 'MEDIUM', 'HIGH']),
                                estimated_loss_rate=flow_rate * 60,  # Convert to L/hr
                                confidence_score=random.uniform(0.7, 0.95)
                            )
                            
                            # Create alert
                            Alert.objects.create(
                                alert_type='LEAK',
                                priority='HIGH' if leak.severity in ['HIGH', 'CRITICAL'] else 'MEDIUM',
                                sensor=sensor,
                                leak=leak,
                                message=f"Potential leak detected at {sensor.location}. Flow: {flow_rate:.1f} L/min"
                            )
                            
                            self.stdout.write(self.style.WARNING(f'LEAK DETECTED: {sensor.device_id}'))
                    
                    # Create reading
                    reading = SensorReading.objects.create(
                        sensor=sensor,
                        flow_rate=round(flow_rate, 2),
                        pressure=round(pressure, 2),
                        temperature=round(random.uniform(20, 30), 1),
                        battery_level=random.randint(75, 100)
                    )
                    
                    readings_generated += 1
                    
                    self.stdout.write(
                        f'{sensor.device_id}: Flow={flow_rate:.2f} L/min, '
                        f'Pressure={pressure:.2f} PSI, '
                        f'Battery={reading.battery_level}%'
                    )
                
                if count == 0 or readings_generated < count:
                    self.stdout.write(f'Waiting {interval} seconds...\n')
                    time.sleep(interval)
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS(f'\nSimulation stopped. Generated {readings_generated} readings.'))