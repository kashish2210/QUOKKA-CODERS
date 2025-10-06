from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Avg, Max, Min, Count
from django.utils import timezone
from datetime import timedelta
from .models import SensorDevice, SensorReading, WaterConsumptionZone

def dashboard(request):
    total_sensors = SensorDevice.objects.count()
    active_sensors = SensorDevice.objects.filter(is_active=True).count()
    
    # Recent readings
    recent_readings = SensorReading.objects.select_related('sensor').all()[:10]
    
    # Get all sensors with latest reading
    sensors = SensorDevice.objects.all()
    
    context = {
        'total_sensors': total_sensors,
        'active_sensors': active_sensors,
        'recent_readings': recent_readings,
        'sensors': sensors,
    }
    return render(request, 'sensors/dashboard.html', context)

def sensor_list(request):
    sensors = SensorDevice.objects.all()
    context = {'sensors': sensors}
    return render(request, 'sensors/sensor_list.html', context)

def sensor_detail(request, device_id):
    sensor = get_object_or_404(SensorDevice, device_id=device_id)
    
    # Get readings from last 24 hours
    since = timezone.now() - timedelta(hours=24)
    readings = sensor.readings.filter(timestamp__gte=since)
    
    # Statistics
    stats = readings.aggregate(
        avg_flow=Avg('flow_rate'),
        max_flow=Max('flow_rate'),
        min_flow=Min('flow_rate'),
        avg_pressure=Avg('pressure'),
        total_readings=Count('id')
    )
    
    context = {
        'sensor': sensor,
        'readings': readings[:50],
        'stats': stats,
    }
    return render(request, 'sensors/sensor_detail.html', context)

def zones_list(request):
    zones = WaterConsumptionZone.objects.all()
    context = {'zones': zones}
    return render(request, 'sensors/zones_list.html', context)

## teerminal:

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import os
import json
import sys
import threading
import queue

# Store the process globally
simulation_process = None
output_queue = queue.Queue()
is_running = False

def terminal_view(request):
    """Render the terminal interface"""
    return render(request, 'terminal.html')

@csrf_exempt
def execute_command(request):
    """Execute terminal commands"""
    if request.method == 'POST':
        data = json.loads(request.body)
        command = data.get('command', '').strip()
        
        if command == 'start simulation' or command == 'python manage.py simulate_sensor':
            return start_simulation()
        elif command == 'stop simulation':
            return stop_simulation()
        elif command == 'status':
            return check_status()
        elif command == 'help':
            return JsonResponse({
                'output': """Available Commands:
  start simulation  - Start the sensor simulation with live output
  stop simulation   - Stop the sensor simulation
  status           - Check simulation status
  help             - Show this help message
  clear            - Clear terminal screen""",
                'success': True
            })
        elif command == 'clear':
            return JsonResponse({'output': '', 'success': True, 'clear': True})
        else:
            return JsonResponse({
                'output': f'Unknown command: {command}\nType "help" for available commands.',
                'success': False
            })
    
    return JsonResponse({'output': 'Invalid request', 'success': False})

def enqueue_output(pipe, queue):
    """Read output from pipe and put in queue"""
    try:
        for line in iter(pipe.readline, ''):
            if line:
                queue.put(line)
        pipe.close()
    except Exception as e:
        queue.put(f"Error reading output: {str(e)}\n")

def start_simulation():
    """Start the sensor simulation process with live output"""
    global simulation_process, is_running, output_queue
    
    if is_running and simulation_process and simulation_process.poll() is None:
        return JsonResponse({
            'output': 'Simulation is already running! Use "stop simulation" to stop it first.',
            'success': False
        })
    
    try:
        # Clear output queue
        while not output_queue.empty():
            try:
                output_queue.get_nowait()
            except queue.Empty:
                break
        
        # Get Python executable
        python_exe = sys.executable
        
        # Start the simulation process with unbuffered output
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        
        # CRITICAL: Use a separate process group to isolate from parent
        if sys.platform == 'win32':
            # Windows: CREATE_NEW_PROCESS_GROUP flag
            simulation_process = subprocess.Popen(
                [python_exe, 'manage.py', 'simulate_sensor', '--interval', '5'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            # Unix/Linux: Use preexec_fn to create new process group
            simulation_process = subprocess.Popen(
                [python_exe, 'manage.py', 'simulate_sensor', '--interval', '5'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env,
                preexec_fn=os.setpgrp  # Create new process group
            )
        
        is_running = True
        
        # Start thread to read output
        output_thread = threading.Thread(
            target=enqueue_output, 
            args=(simulation_process.stdout, output_queue),
            daemon=True
        )
        output_thread.start()
        
        return JsonResponse({
            'output': '✓ Sensor simulation started!\n\nLive output streaming...\n' + '='*50,
            'success': True,
            'streaming': True
        })
    except Exception as e:
        is_running = False
        return JsonResponse({
            'output': f'Error starting simulation: {str(e)}',
            'success': False
        })

@csrf_exempt
def get_output(request):
    """Get buffered output from simulation"""
    global output_queue, simulation_process, is_running
    
    if request.method == 'GET':
        lines = []
        
        # Get all available output from queue
        while not output_queue.empty():
            try:
                line = output_queue.get_nowait()
                lines.append(line.rstrip())
            except queue.Empty:
                break
        
        # Check if process is still running
        if simulation_process:
            if simulation_process.poll() is not None:
                is_running = False
        
        output = '\n'.join(lines) if lines else ''
        
        return JsonResponse({
            'output': output,
            'is_running': is_running
        })
    
    return JsonResponse({'output': '', 'is_running': False})

def stop_simulation():
    """Stop the sensor simulation process"""
    global simulation_process, is_running, output_queue
    
    if not is_running or not simulation_process:
        return JsonResponse({
            'output': 'No simulation is currently running.',
            'success': False
        })
    
    try:
        is_running = False
        
        # FIXED: Use terminate() instead of sending signals
        # This safely stops only the child process without affecting Django server
        simulation_process.terminate()
        
        # Wait for graceful shutdown
        try:
            simulation_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            # Force kill if it doesn't terminate gracefully
            simulation_process.kill()
            simulation_process.wait(timeout=2)
        
        # Collect remaining output
        remaining_lines = []
        while not output_queue.empty():
            try:
                line = output_queue.get_nowait()
                remaining_lines.append(line.rstrip())
            except queue.Empty:
                break
        
        final_output = '\n'.join(remaining_lines) if remaining_lines else ''
        
        simulation_process = None
        
        return JsonResponse({
            'output': final_output + '\n\n' + '='*50 + '\n✓ Sensor simulation stopped successfully!',
            'success': True
        })
    except Exception as e:
        is_running = False
        simulation_process = None
        return JsonResponse({
            'output': f'Error stopping simulation: {str(e)}',
            'success': False
        })

def check_status():
    """Check if simulation is running"""
    global is_running, simulation_process
    
    # Update running status based on process state
    if simulation_process:
        if simulation_process.poll() is not None:
            is_running = False
    
    if is_running and simulation_process:
        return JsonResponse({
            'output': f'● Simulation Status: RUNNING\n\nProcess ID: {simulation_process.pid}\nInterval: 5 seconds\nMode: Live streaming\n\nGenerating sensor readings...',
            'success': True
        })
    else:
        return JsonResponse({
            'output': '● Simulation Status: STOPPED\n\nNo active simulation process.\nUse "start simulation" to begin.',
            'success': True
        })