import machine
import time
import urequests  # MicroPython library for HTTP requests
from machine import Pin

# Wi-Fi Credentials
ssid = 'Redmi'
password = '876543210'

# Define pins for the JSN-SR04T sensor
TRIG_PIN = 12   # Change to your GPIO pin for Trig
ECHO_PIN = 14   # Change to your GPIO pin for Echo
LED = Pin(26, Pin.OUT)

# Define URL for your Node.js server
nodejs_server_url = 'https://test-iot-554d.onrender.com/sensor-distance'

# Function to connect to Wi-Fi
def connect_wifi():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    while not wlan.isconnected():
        time.sleep(1)
        print('Connecting to Wi-Fi...')

    print('Connected to Wi-Fi')
    print('Network config:', wlan.ifconfig())

# Function to measure distance
def measure_distance():
    trig = machine.Pin(TRIG_PIN, machine.Pin.OUT)
    echo = machine.Pin(ECHO_PIN, machine.Pin.IN)

    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    # Measure the duration of the pulse
    timeout = 10000  # Timeout value in microseconds
    start_time = time.ticks_us()

    while echo.value() == 0:
        if time.ticks_diff(time.ticks_us(), start_time) > timeout:
            return -1  # Return -1 for timeout (sensor not working)
    
    start = time.ticks_us()

    while echo.value() == 1:
        if time.ticks_diff(time.ticks_us(), start) > timeout:
            return -1  # Return -1 for timeout (sensor not working)

    end = time.ticks_us()

    # Calculate distance in centimeters
    duration = time.ticks_diff(end, start)
    distance = (duration / 2) / 29.1  # Speed of sound = 343 m/s
    return int(distance)

# Connect to Wi-Fi
connect_wifi()

while True:
    # Measure distance from the sensor
    distance = measure_distance()

    if distance == -1:
        status = "off"  # Sensor not working
        print("Sensor not responding")
    else:
        status = "on"  # Sensor working
        print(f'Distance: {distance} cm')

    # Control the LED based on distance
    if distance <= 50 and distance != -1:
        LED.value(1)  # Turn on LED if distance is <= 50 cm
        binLid_status = "OPEN"
    else:
        LED.value(0)  # Turn off LED otherwise
        binLid_status = "CLOSED"

    # Prepare dynamic data to send to the Node.js server
    obj = {
        "_id": 1,
        "binLid_status": binLid_status,
        "distance": distance,
        "location": "Auditorium",
        "microProcessor_status": "ON",
        "sensor_status": status.upper()
    }

#     try:
#         response = urequests.post(nodejs_server_url, json=obj)
#         print(f'Status: {response.status_code}, Response: {response.text}')
#         response.close()
#     except Exception as e:
#         print('Error sending data:', e)
    print(obj)

    time.sleep(1)  # Send data every second
