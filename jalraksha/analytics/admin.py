from django.contrib import admin
from .models import LeakDetection, ConsumptionPattern

@admin.register(LeakDetection)
class LeakDetectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'sensor', 'detected_at', 'severity', 'status', 'estimated_loss_rate']
    list_filter = ['severity', 'status', 'detected_at']
    search_fields = ['sensor__device_id', 'sensor__location']

@admin.register(ConsumptionPattern)
class ConsumptionPatternAdmin(admin.ModelAdmin):
    list_display = ['sensor', 'date', 'total_consumption', 'continuous_flow_detected']
    list_filter = ['date', 'continuous_flow_detected']