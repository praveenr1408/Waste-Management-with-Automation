import machine
import time
import urequests  # MicroPython library for HTTP requests
from machine import Pin

# Wi-Fi Credentials
ssid = 'Redmi'
password = '876543210'

# Define pins for the AJ-SR04M sensor
TRIG_PIN = 13   # Change to your GPIO pin for Trig
ECHO_PIN = 12   # Change to your GPIO pin for Echo
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
    timeout = 20000  # Adjusted Timeout value in microseconds
    start_time = time.ticks_us()

    while echo.value() == 0:
        if time.ticks_diff(time.ticks_us(), start_time) > timeout:
            return None  # Return None for timeout (sensor not working)

    start = time.ticks_us()

    while echo.value() == 1:
        if time.ticks_diff(time.ticks_us(), start) > timeout:
            return None  # Return None for timeout (sensor not working)

    end = time.ticks_us()

    # Calculate distance in centimeters
    duration = time.ticks_diff(end, start)
    distance = (duration / 2) / 29.1  # Speed of sound = 343 m/s
    return int(distance)

# Connect to Wi-Fi
connect_wifi()

# Initialize variables
previous_distance = None  # To track previous distance measurement
distance_threshold = 5    # Define a threshold for distance change
status_update_interval = 10  # 10 seconds for faster status update
last_status_update_time = time.time()  # Record the last status update time

while True:
    # Measure distance from the sensor
    distance = measure_distance()

    if distance is None:
        print("Sensor not responding")
        # Skip sending data if the sensor is not responding
        continue
    else:
        status = "on"  # Sensor working
        print(f'Distance: {distance} cm')

    # Control the LED based on distance
    if distance <= 50:
        LED.value(1)  # Turn on LED if distance is <= 50 cm
        binLid_status = "OPEN"
    else:
        LED.value(0)  # Turn off LED otherwise
        binLid_status = "CLOSED"

    current_time = time.time()

    # Send status update every 10 seconds
    if current_time - last_status_update_time >= status_update_interval:
        # Prepare dynamic data to send to the Node.js server
        status_obj = {
            "type": "distance",  # Keep type as "distance"
            "id": 1,
            "binLid_status": binLid_status,
            "distance": distance,
            "location": "Canteen",
            "microProcessor_status": "ON",
            "sensor_status": status
        }

        try:
            response = urequests.post(nodejs_server_url, json=status_obj)
            print(f'Status update sent: {response.status_code}, Response: {response.text}')
            response.close()
        except Exception as e:
            print('Error sending status update:', e)

        print(status_obj)

        # Update last status update time
        last_status_update_time = current_time

    # Only send distance data if the distance has changed by more than the threshold
    if previous_distance is None or abs(previous_distance - distance) > distance_threshold:
        # Prepare dynamic data to send to the Node.js server
        distance_obj = {
            "type": "distance",  # Keep type as "distance"
            "id": 1,
            "binLid_status": binLid_status,
            "distance": distance,
            "location": "Canteen",
            "microProcessor_status": "ON",
            "sensor_status": status
        }

#         try:
#             response = urequests.post(nodejs_server_url, json=distance_obj)
#             print(f'Status: {response.status_code}, Response: {response.text}')
#             response.close()
#         except Exception as e:
#             print('Error sending distance data:', e)

        print(distance_obj)

        # Update the previous distance
        previous_distance = distance

    time.sleep(1)  # Check every second for distance changes
