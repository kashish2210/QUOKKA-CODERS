from django.contrib import admin
from .models import SensorDevice, SensorReading, WaterConsumptionZone

@admin.register(SensorDevice)
class SensorDeviceAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'sensor_type', 'deployment_type', 'location', 'is_active']
    list_filter = ['sensor_type', 'deployment_type', 'is_active']
    search_fields = ['device_id', 'location']

@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ['sensor', 'timestamp', 'flow_rate', 'pressure', 'temperature', 'battery_level']
    list_filter = ['sensor', 'timestamp']
    date_hierarchy = 'timestamp'

@admin.register(WaterConsumptionZone)
class WaterConsumptionZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'zone_type', 'contact_person', 'contact_email']
    filter_horizontal = ['sensors']