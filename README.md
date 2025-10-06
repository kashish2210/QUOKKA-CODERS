<img width="1912" height="556" alt="image" src="https://github.com/user-attachments/assets/76b8b941-6105-4ecc-8956-b2a67afa3354" /># JalRaksha - AI-Driven Water Conservation Platform

Django-based water management system with IoT sensor monitoring and AI-powered leak detection.

## Prerequisites

- Python 3.8+
- pip
- virtualenv

## Quick Start

### 1. Create Project

```bash
mkdir jalraksha
cd jalraksha
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install django djangorestframework
```

### 4. Create Django Project

```bash
django-admin startproject jalraksha .
python manage.py startapp sensors
python manage.py startapp analytics
python manage.py startapp alerts
```

### 5. Create Directory Structure

**Windows:**
```bash
mkdir templates templates\sensors templates\analytics templates\alerts
mkdir static static\css static\js
mkdir sensors\management sensors\management\commands
type nul > sensors\management\__init__.py
type nul > sensors\management\commands\__init__.py
```

**Linux/Mac:**
```bash
mkdir -p templates/{sensors,analytics,alerts}
mkdir -p static/{css,js}
mkdir -p sensors/management/commands
touch sensors/management/__init__.py
touch sensors/management/commands/__init__.py
```

## Configuration

### Update jalraksha/settings.py

1. Add apps to INSTALLED_APPS:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'sensors',
    'analytics',
    'alerts',
]
```

2. Configure templates:
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

3. Configure static files:
```python
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

4. Set timezone:
```python
TIME_ZONE = 'Asia/Kolkata'
```

### Update jalraksha/urls.py

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sensors.urls')),
    path('analytics/', include('analytics.urls')),
    path('alerts/', include('alerts.urls')),
    path('api/', include('sensors.api_urls')),
]
```

## Files to Copy

Copy all files from the artifacts into their respective locations:

### Models
- Copy models from artifact to `sensors/models.py`
- Copy models from artifact to `analytics/models.py`
- Copy models from artifact to `alerts/models.py`

### Views
- Copy views from artifact to `sensors/views.py`
- Copy views from artifact to `analytics/views.py`
- Copy views from artifact to `alerts/views.py`

### URLs
- Copy URLs from artifact to `sensors/urls.py`
- Copy URLs from artifact to `analytics/urls.py`
- Copy URLs from artifact to `alerts/urls.py`
- Copy API URLs from artifact to `sensors/api_urls.py`

### Admin
- Copy admin from artifact to `sensors/admin.py`
- Copy admin from artifact to `analytics/admin.py`
- Copy admin from artifact to `alerts/admin.py`

### API
- Copy serializers from artifact to `sensors/serializers.py`
- Copy API views from artifact to `sensors/api_views.py`

### Management Command
- Copy simulate_sensor.py to `sensors/management/commands/simulate_sensor.py`

### Templates
Copy all HTML files from artifacts to templates directory:
- base.html
- header.html
- footer.html
- sensors/*.html
- analytics/*.html
- alerts/*.html

### Static Files
- Copy CSS from artifact to `static/css/style.css`
- Copy JS from artifact to `static/js/main.js`

## Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

## Create Superuser

```bash
python manage.py createsuperuser
```

Enter username, email, and password when prompted.

## Run Development Server

```bash
python manage.py runserver
```

Access the application at: http://127.0.0.1:8000/

## Initial Setup

### 1. Login to Admin Panel

Navigate to: http://127.0.0.1:8000/admin/

### 2. Add Sensors

Go to Sensors > Sensor devices > Add sensor device

Example sensors to add:

**Sensor 1:**
- Device ID: SENSOR001
- Sensor type: Ultrasonic Flow Sensor
- Deployment type: Municipal Distribution
- Location: Main Road, Sector 5
- Is active: Yes

**Sensor 2:**
- Device ID: SENSOR002
- Sensor type: Pressure Sensor
- Deployment type: Residential Society
- Location: Residential Complex A, Block 2
- Is active: Yes

**Sensor 3:**
- Device ID: SENSOR003
- Sensor type: Ultrasonic Flow Sensor
- Deployment type: Municipal Distribution
- Location: Water Treatment Plant, Zone 3
- Is active: Yes

### 3. Start Sensor Simulation

Open a new terminal, activate venv, and run:

```bash
python manage.py simulate_sensor
```

This will generate sensor readings every 5 seconds.

Options:
```bash
# Generate 10 readings only
python manage.py simulate_sensor --count 10

# Change interval to 10 seconds
python manage.py simulate_sensor --interval 10
```

## Project Features

### Dashboard
- Real-time sensor monitoring
- Active sensor count
- Recent readings display
- System statistics

### Sensors Module
- Sensor device management
- Real-time readings
- 24-hour statistics
- Device location tracking

### Analytics Module
- Leak detection with AI
- Severity classification
- Water loss estimation
- Consumption pattern analysis

### Alerts Module
- Real-time alerts
- Priority-based notifications
- Alert filtering
- Resolution tracking

## API Endpoints

### Sensors
- GET /api/sensors/ - List all sensors
- POST /api/sensors/ - Create sensor
- GET /api/sensors/{id}/ - Get sensor details
- GET /api/sensors/{id}/recent_readings/ - Get recent readings

### Readings
- GET /api/readings/ - List all readings
- POST /api/readings/ - Create reading (for IoT devices)

### Example API Usage

**Create Reading:**
```bash
curl -X POST http://127.0.0.1:8000/api/readings/ \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "SENSOR001",
    "flow_rate": 25.5,
    "pressure": 45.2,
    "temperature": 24.5,
    "battery_level": 95
  }'
```

## Project Structure

```
jalraksha/
├── manage.py
├── db.sqlite3
├── jalraksha/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── sensors/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── serializers.py
│   ├── api_views.py
│   └── api_urls.py
├── analytics/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── alerts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── templates/
│   ├── base.html
│   ├── header.html
│   ├── footer.html
│   ├── sensors/
│   ├── analytics/
│   └── alerts/
└── static/
    ├── css/
    └── js/
```

## Navigation

- Dashboard: http://127.0.0.1:8000/
- Sensors: http://127.0.0.1:8000/sensors/
- Analytics: http://127.0.0.1:8000/analytics/
- Alerts: http://127.0.0.1:8000/alerts/
- Admin: http://127.0.0.1:8000/admin/

## Troubleshooting

### Import Errors
Make sure __init__.py files exist in management and commands directories.

### Template Not Found
Check DIRS in TEMPLATES settings points to BASE_DIR / 'templates'

### Static Files Not Loading
Run `python manage.py collectstatic` if needed.

### No Sensors Found
Add sensors through admin panel before running simulation.

## Next Steps

1. Add more sensors through admin panel
2. Run sensor simulation to generate data
3. Monitor analytics dashboard for leak detection
4. Check alerts for notifications
5. Future: Integrate real ESP32/IoT hardware
## screenshots
### dummy sensor simulator command:
<img width="796" height="200" alt="image" src="https://github.com/user-attachments/assets/08af0038-4fbd-46db-ad3d-26d2dcba49f9" />
### SENSOR DASHBOARD:
<img width="1894" height="921" alt="image" src="https://github.com/user-attachments/assets/1b5e0ac4-3f8e-4053-8952-a6e8585138fc" />
<img width="1897" height="835" alt="image" src="https://github.com/user-attachments/assets/81cf5e6e-7c62-4de1-bdb5-ea96d5e2a889" />
### ANALYTICS DASHBOARD:
<img width="1889" height="882" alt="image" src="https://github.com/user-attachments/assets/1251634d-1019-4b4d-aa81-d8e6c6a8eb04" />
<img width="1885" height="877" alt="image" src="https://github.com/user-attachments/assets/a5a90cef-ba78-4ae9-8913-11a8b060a568" />
<img width="1900" height="875" alt="image" src="https://github.com/user-attachments/assets/cea239f6-44ae-4e91-9a99-bd6b0c8cec64" />
<img width="1827" height="804" alt="image" src="https://github.com/user-attachments/assets/a78e5205-7ee6-4e87-b3e2-2f2cd9069c5e" />
<img width="1894" height="873" alt="image" src="https://github.com/user-attachments/assets/90abb782-4cb6-4b23-8a76-8755ad3d9980" />
### ALERTS
<img width="1895" height="904" alt="image" src="https://github.com/user-attachments/assets/44321d06-4526-4734-b2e4-8c5afe04874c" />
### ADD NEW SENSORS
<img width="1897" height="858" alt="image" src="https://github.com/user-attachments/assets/7f1e7c41-2bcc-4c01-ba7b-cd43d5f1fcab" />
<img width="1912" height="885" alt="image" src="https://github.com/user-attachments/assets/37390f0c-5192-429d-8c4e-840c01b853cd" />
### our terminal {new feature}
<img width="1908" height="898" alt="image" src="https://github.com/user-attachments/assets/cb15feb4-1364-459d-96a7-9520b94cb051" />
<img width="1912" height="556" alt="image" src="https://github.com/user-attachments/assets/8e9d0d20-41aa-405c-99ba-b1a3bf0a252a" />
<img width="1908" height="543" alt="image" src="https://github.com/user-attachments/assets/492a5e63-709b-4d8b-bec6-69110221f921" />
<img width="1907" height="375" alt="image" src="https://github.com/user-attachments/assets/efb92881-8010-46e8-a159-7e6224dc1895" />
## Team

Quokka Coders - NavonMesh Hackathon

## License

Educational Project for Water Management

## for future implementation with ESP32 visit [here](https://github.com/kashish2210/QUOKKA-CODERS/blob/main/blueprint_esp32.md)
