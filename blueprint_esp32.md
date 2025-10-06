# ESP32 Integration Blueprint

Complete guide to integrate ESP32 with JalRaksha Django backend for real IoT water monitoring.

## Hardware Requirements

### Components Needed:
1. ESP32 Development Board (ESP32-WROOM-32)
2. Ultrasonic Flow Sensor (YF-S201 or similar)
3. Pressure Sensor (0-1.2 MPa sensor with analog output)
4. Breadboard and jumper wires
5. 5V Power supply
6. Micro USB cable for programming

### Optional Components:
- DHT11/DHT22 Temperature sensor
- LCD Display (16x2) for local readings
- LED indicators for status

## Hardware Connections

### Flow Sensor (YF-S201) Connections:
```
YF-S201          ESP32
--------         -----
RED    (VCC) --> 5V
BLACK  (GND) --> GND
YELLOW (SIG) --> GPIO 4
```

### Pressure Sensor Connections:
```
Pressure Sensor  ESP32
---------------  -----
VCC          --> 3.3V
GND          --> GND
OUT          --> GPIO 34 (ADC1_CH6)
```

### Optional Temperature Sensor (DHT11):
```
DHT11            ESP32
-----            -----
VCC          --> 3.3V
GND          --> GND
DATA         --> GPIO 5
```

### LED Indicators (Optional):
```
LED              ESP32
---              -----
Green (WiFi) --> GPIO 2
Red (Error)  --> GPIO 15
Blue (Send)  --> GPIO 13
```

## Pin Configuration Summary

| Component | ESP32 Pin | Type |
|-----------|-----------|------|
| Flow Sensor | GPIO 4 | Digital Input |
| Pressure Sensor | GPIO 34 | Analog Input |
| Temperature Sensor | GPIO 5 | Digital Input |
| WiFi LED | GPIO 2 | Output |
| Error LED | GPIO 15 | Output |
| Send LED | GPIO 13 | Output |

## Arduino IDE Setup

### 1. Install Arduino IDE
Download from: https://www.arduino.cc/en/software

### 2. Add ESP32 Board Support

**Step 1:** Open Arduino IDE
**Step 2:** Go to File > Preferences
**Step 3:** Add this URL to "Additional Board Manager URLs":
```
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
```

**Step 4:** Go to Tools > Board > Boards Manager
**Step 5:** Search for "esp32" and install "esp32 by Espressif Systems"

### 3. Install Required Libraries

Go to Sketch > Include Library > Manage Libraries

Install these libraries:
- **WiFi** (Built-in with ESP32)
- **HTTPClient** (Built-in with ESP32)
- **ArduinoJson** by Benoit Blanchon (Version 6.x)
- **DHT sensor library** by Adafruit (if using temperature sensor)

### 4. Select Board

Go to Tools and select:
- Board: "ESP32 Dev Module"
- Upload Speed: "115200"
- CPU Frequency: "240MHz"
- Flash Frequency: "80MHz"
- Flash Mode: "QIO"
- Flash Size: "4MB"
- Port: Select your COM port

## ESP32 Code

### Complete Arduino Code:

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi Configuration
const char* ssid = "YOUR_WIFI_SSID";           // Replace with your WiFi name
const char* password = "YOUR_WIFI_PASSWORD";   // Replace with your WiFi password

// Django Server Configuration
const char* serverUrl = "http://YOUR_PC_IP:8000/api/readings/";  // Replace YOUR_PC_IP
const char* deviceId = "SENSOR001";  // Match with Django database

// Pin Definitions
#define FLOW_SENSOR_PIN 4
#define PRESSURE_SENSOR_PIN 34
#define TEMP_SENSOR_PIN 5
#define WIFI_LED 2
#define ERROR_LED 15
#define SEND_LED 13

// Flow Sensor Variables
volatile int flowPulseCount = 0;
float flowRate = 0.0;
unsigned long oldTime = 0;
const float calibrationFactor = 4.5;  // Calibrate based on your sensor

// Sensor Reading Interval
const unsigned long READING_INTERVAL = 5000;  // 5 seconds
unsigned long lastReadingTime = 0;

void IRAM_ATTR flowPulseCounter() {
  flowPulseCount++;
}

void setup() {
  Serial.begin(115200);
  
  // Pin Modes
  pinMode(FLOW_SENSOR_PIN, INPUT_PULLUP);
  pinMode(PRESSURE_SENSOR_PIN, INPUT);
  pinMode(WIFI_LED, OUTPUT);
  pinMode(ERROR_LED, OUTPUT);
  pinMode(SEND_LED, OUTPUT);
  
  // Attach interrupt for flow sensor
  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN), flowPulseCounter, FALLING);
  
  // Initial LED states
  digitalWrite(WIFI_LED, LOW);
  digitalWrite(ERROR_LED, LOW);
  digitalWrite(SEND_LED, LOW);
  
  // Connect to WiFi
  connectWiFi();
  
  Serial.println("JalRaksha Sensor Initialized");
  Serial.println("Device ID: " + String(deviceId));
}

void loop() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    digitalWrite(WIFI_LED, LOW);
    digitalWrite(ERROR_LED, HIGH);
    connectWiFi();
    return;
  }
  
  digitalWrite(WIFI_LED, HIGH);
  digitalWrite(ERROR_LED, LOW);
  
  // Read sensors at specified interval
  if (millis() - lastReadingTime >= READING_INTERVAL) {
    lastReadingTime = millis();
    
    // Read all sensors
    float flow = readFlowSensor();
    float pressure = readPressureSensor();
    float temperature = readTemperature();
    int battery = readBatteryLevel();
    
    // Display readings on Serial Monitor
    printReadings(flow, pressure, temperature, battery);
    
    // Send data to Django server
    sendDataToServer(flow, pressure, temperature, battery);
  }
}

void connectWiFi() {
  Serial.println("\nConnecting to WiFi...");
  Serial.print("SSID: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    digitalWrite(WIFI_LED, !digitalRead(WIFI_LED));  // Blink LED
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    digitalWrite(WIFI_LED, HIGH);
  } else {
    Serial.println("\nWiFi Connection Failed!");
    digitalWrite(ERROR_LED, HIGH);
  }
}

float readFlowSensor() {
  // Calculate flow rate from pulse count
  if ((millis() - oldTime) > 1000) {
    detachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN));
    
    // Flow rate calculation
    flowRate = ((1000.0 / (millis() - oldTime)) * flowPulseCount) / calibrationFactor;
    
    oldTime = millis();
    flowPulseCount = 0;
    
    attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN), flowPulseCounter, FALLING);
  }
  
  return flowRate;
}

float readPressureSensor() {
  // Read analog value from pressure sensor
  int analogValue = analogRead(PRESSURE_SENSOR_PIN);
  
  // Convert to PSI (adjust formula based on your sensor)
  // For 0-1.2MPa sensor: 0-1.2MPa = 0-174 PSI
  // Assuming 0-4095 ADC range maps to 0-174 PSI
  float pressure = (analogValue / 4095.0) * 174.0;
  
  return pressure;
}

float readTemperature() {
  // For now, return a simulated value
  // Replace with actual DHT11/DHT22 reading if connected
  return 25.0 + random(-5, 5);  // 20-30°C range
}

int readBatteryLevel() {
  // For now, return 100% (can be replaced with actual battery monitoring)
  return 100;
}

void printReadings(float flow, float pressure, float temp, int battery) {
  Serial.println("\n--- Sensor Readings ---");
  Serial.print("Device ID: ");
  Serial.println(deviceId);
  Serial.print("Flow Rate: ");
  Serial.print(flow);
  Serial.println(" L/min");
  Serial.print("Pressure: ");
  Serial.print(pressure);
  Serial.println(" PSI");
  Serial.print("Temperature: ");
  Serial.print(temp);
  Serial.println(" °C");
  Serial.print("Battery: ");
  Serial.print(battery);
  Serial.println("%");
  Serial.println("----------------------");
}

void sendDataToServer(float flow, float pressure, float temp, int battery) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected. Skipping upload.");
    return;
  }
  
  digitalWrite(SEND_LED, HIGH);
  
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  
  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["device_id"] = deviceId;
  doc["flow_rate"] = flow;
  doc["pressure"] = pressure;
  doc["temperature"] = temp;
  doc["battery_level"] = battery;
  
  String jsonData;
  serializeJson(doc, jsonData);
  
  Serial.println("\nSending to server: " + jsonData);
  
  // Send POST request
  int httpResponseCode = http.POST(jsonData);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("HTTP Response Code: " + String(httpResponseCode));
    Serial.println("Server Response: " + response);
    
    // Blink send LED on success
    for (int i = 0; i < 3; i++) {
      digitalWrite(SEND_LED, LOW);
      delay(100);
      digitalWrite(SEND_LED, HIGH);
      delay(100);
    }
  } else {
    Serial.print("Error sending data. HTTP Code: ");
    Serial.println(httpResponseCode);
    digitalWrite(ERROR_LED, HIGH);
    delay(1000);
    digitalWrite(ERROR_LED, LOW);
  }
  
  digitalWrite(SEND_LED, LOW);
  http.end();
}
```

## Configuration Steps

### 1. Update WiFi Credentials

In the code, replace:
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
```

### 2. Get Your PC IP Address

**Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address" under your WiFi adapter (e.g., 192.168.1.100)

**Linux/Mac:**
```bash
ifconfig
```
Look for inet address

### 3. Update Server URL

Replace in code:
```cpp
const char* serverUrl = "http://192.168.1.100:8000/api/readings/";
```
Use your PC's IP address

### 4. Match Device ID

Make sure the Device ID in ESP32 code matches a sensor in Django admin:
```cpp
const char* deviceId = "SENSOR001";  // Must exist in Django database
```

## Upload and Test

### 1. Connect ESP32 to PC
- Connect ESP32 via USB cable
- Select correct COM port in Arduino IDE

### 2. Upload Code
- Click Upload button (→) in Arduino IDE
- Wait for "Done uploading" message

### 3. Open Serial Monitor
- Tools > Serial Monitor
- Set baud rate to 115200
- You should see:
```
Connecting to WiFi...
WiFi Connected!
IP Address: 192.168.1.150
JalRaksha Sensor Initialized
Device ID: SENSOR001

--- Sensor Readings ---
Device ID: SENSOR001
Flow Rate: 25.43 L/min
Pressure: 45.21 PSI
Temperature: 24.5 °C
Battery: 100%
----------------------
Sending to server: {"device_id":"SENSOR001",...}
HTTP Response Code: 201
Server Response: {...}
```

### 4. Verify on Django Dashboard
- Open: http://127.0.0.1:8000/
- You should see real readings from ESP32

## Troubleshooting

### WiFi Connection Issues:
- Check SSID and password are correct
- Ensure ESP32 and PC are on same network
- Check WiFi signal strength

### Server Connection Issues:
- Verify Django server is running
- Check PC IP address is correct
- Disable PC firewall temporarily for testing
- Ensure PC and ESP32 are on same WiFi network

### No Flow Sensor Reading:
- Check sensor connections
- Verify water is flowing through sensor
- Adjust calibrationFactor value

### Wrong Pressure Reading:
- Check analog pin connection
- Calibrate pressure formula for your sensor
- Verify sensor voltage (3.3V or 5V)

## Sensor Calibration

### Flow Sensor Calibration:
1. Measure actual water flow with a container
2. Compare with sensor reading
3. Adjust `calibrationFactor` in code:
```cpp
const float calibrationFactor = 4.5;  // Adjust this value
```

### Pressure Sensor Calibration:
1. Use known pressure source
2. Measure analog reading
3. Adjust formula in `readPressureSensor()`:
```cpp
float pressure = (analogValue / 4095.0) * MAX_PRESSURE;
```

## Power Options

### USB Power:
- Connect to PC or USB charger
- Good for testing

### Battery Power:
- Use 5V power bank
- Add battery monitoring circuit
- Update `readBatteryLevel()` function

### Solar Power:
- Use 5V solar panel with battery
- Add charging circuit
- Good for outdoor deployment

## Next Steps

1. Test with single ESP32 first
2. Calibrate sensors with actual water flow
3. Deploy multiple ESP32 devices
4. Monitor from Django dashboard
5. Set up alerts for leak detection

## Multiple Sensor Deployment

To deploy multiple sensors:

1. Copy the code for each ESP32
2. Change only the Device ID:
```cpp
const char* deviceId = "SENSOR002";  // Unique for each ESP32
```
3. Create corresponding sensors in Django admin
4. Upload code to each ESP32

## Production Deployment

For production:
1. Use static IP for Django server
2. Set up proper domain name
3. Enable HTTPS for security
4. Add authentication to API
5. Use external database (PostgreSQL)
6. Deploy Django on cloud server
7. Add data encryption

## Cost Estimate

| Component | Quantity | Price (INR) |
|-----------|----------|-------------|
| ESP32 | 1 | 400 |
| Flow Sensor | 1 | 300 |
| Pressure Sensor | 1 | 250 |
| Wires & Breadboard | 1 | 150 |
| Power Supply | 1 | 200 |
| **Total per unit** | | **1300** |

## Support

For issues or questions:
- Check Serial Monitor output
- Verify Django API endpoint
- Test API with Postman first
- Check sensor datasheets for specifications