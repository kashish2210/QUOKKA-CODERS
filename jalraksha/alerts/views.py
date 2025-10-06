from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Alert

def alerts_list(request):
    filter_type = request.GET.get('type', 'all')
    
    if filter_type == 'unread':
        alerts = Alert.objects.filter(is_read=False)
    elif filter_type == 'unresolved':
        alerts = Alert.objects.filter(is_resolved=False)
    else:
        alerts = Alert.objects.all()
    
    alerts = alerts.select_related('sensor', 'leak')
    
    context = {
        'alerts': alerts,
        'filter_type': filter_type,
        'unread_count': Alert.objects.filter(is_read=False).count(),
        'unresolved_count': Alert.objects.filter(is_resolved=False).count(),
    }
    return render(request, 'alerts/alerts_list.html', context)

def alert_detail(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    
    # Mark as read
    if not alert.is_read:
        alert.is_read = True
        alert.save()
    
    context = {'alert': alert}
    return render(request, 'alerts/alert_detail.html', context)

def mark_resolved(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    alert.is_resolved = True
    alert.save()
    messages.success(request, 'Alert marked as resolved.')
    return redirect('alerts:alerts_list')