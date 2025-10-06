from django.contrib import admin
from .models import Alert

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['id', 'alert_type', 'priority', 'sensor', 'created_at', 'is_read', 'is_resolved']
    list_filter = ['alert_type', 'priority', 'is_read', 'is_resolved', 'created_at']
    search_fields = ['message', 'sensor__device_id', 'sensor__location']
    actions = ['mark_as_read', 'mark_as_resolved']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)