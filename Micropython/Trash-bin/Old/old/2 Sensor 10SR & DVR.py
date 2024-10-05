import machine
import time
import urequests  # MicroPython library for HTTP requests
from machine import Pin, PWM

binMaxCapacity = 50
# Wi-Fi Credentials
ssid = 'Redmi'
password = '876543210'

# Define pins for the AJ-SR04M (waste level) sensor
TRIG_PIN_AJ = 13  # GPIO pin for Trig (AJ-SR04M)
ECHO_PIN_AJ = 12  # GPIO pin for Echo (AJ-SR04M)

# Define pins for the HC-SR04 (dustbin lid control) sensor
TRIG_PIN_HC = 33  # GPIO pin for Trig (HC-SR04)
ECHO_PIN_HC = 32  # GPIO pin for Echo (HC-SR04)

# Define pin for the LED and Servo Motor
LED = Pin(26, Pin.OUT)
servo_pin = PWM(Pin(25), freq=50)  # Servo motor pin (50 Hz PWM for servo)

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
    

# Function to measure distance from a given trig and echo pin
def measure_distance(trig_pin, echo_pin):
    trig = Pin(trig_pin, Pin.OUT)  # Set Trig pin as output
    echo = Pin(echo_pin, Pin.IN)   # Set Echo pin as input

    # Trigger the sensor
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    # Measure the duration of the pulse
    timeout = 20000  # Timeout value in microseconds
    start_time = time.ticks_us()

    # Wait for echo start
    while echo.value() == 0:
        if time.ticks_diff(time.ticks_us(), start_time) > timeout:
            print("AJ-SR04M Echo timeout (start)")
            return -1  # Return -1 to indicate the sensor is not responding

    start = time.ticks_us()

    # Wait for echo end
    while echo.value() == 1:
        if time.ticks_diff(time.ticks_us(), start) > timeout:
            print("AJ-SR04M Echo timeout (end)")
            return -1  # Return -1 to indicate the sensor is not responding

    end = time.ticks_us()

    # Calculate distance in centimeters
    duration = time.ticks_diff(end, start)
    distance = (duration / 2) / 29.1  # Speed of sound = 343 m/s
    return int(distance)

# Separate functions for measuring distances
def measure_waste_level():
    return measure_distance(TRIG_PIN_AJ, ECHO_PIN_AJ)

def measure_lid_distance():
    return measure_distance(TRIG_PIN_HC, ECHO_PIN_HC)

# Function to control the servo motor (open/close bin lid)
def control_servo(position):
    if position == "OPEN":
        servo_pin.duty(125)  # Adjust duty value for your servo to open the lid
        LED.value(1)        # Turn on LED when the lid is open
    elif position == "CLOSED":
        servo_pin.duty(30)  # Adjust duty value for your servo to close the lid
        LED.value(0)         # Turn off LED when the lid is closed
        

def calculate_percentage(distance):
    full_bin_distance = 20  # Distance for 100% (full)
    empty_bin_distance = binMaxCapacity  # Distance for 0% (empty)

    if distance <= full_bin_distance:
        return 100  # Bin is full
    elif distance >= empty_bin_distance:
        return 0  # Bin is empty
    else:
        percentage = int(((empty_bin_distance - distance) / (empty_bin_distance - full_bin_distance)) * 100)
        return max(0, min(percentage, 100))  # Ensure it's within 0 to 100

# Connect to Wi-Fi
connect_wifi()

# Initialize variables
previous_distance_aj = None  # To track previous distance measurement for AJ-SR04M
previous_distance_hc = None  # To track previous distance measurement for HC-SR04
distance_threshold = 5        # Define a threshold for distance change
status_update_interval = 10   # Status update interval (seconds)
last_status_update_time = time.time()  # Record last status update time

while True:
    # Measure distance from AJ-SR04M (waste level sensor)
    distance_aj = measure_waste_level()

    # Initialize sensor status
    if distance_aj == -1:
        waste_level_sensor_status = "OFF"
        print("AJ-SR04M sensor not responding")
        LED.value(0)  # Turn off LED if the sensor is not working
    else:
        waste_level_sensor_status = "ON"
        print(f'Waste Level Distance: {distance_aj} cm')

    # Control the LED based on AJ-SR04M distance
#     if distance_aj >= 0 and distance_aj <= 50:
#         LED.value(1)  # Turn on LED if waste level is <= 50 cm
#         binLid_status = "OPEN"
#     else:
#         LED.value(0)  # Turn off LED if waste level is > 50 cm
#         binLid_status = "CLOSED"

    # Measure distance from HC-SR04 (lid control sensor)
    distance_hc = measure_lid_distance()

    if distance_hc == -1:
        print("HC-SR04 sensor not responding")
        continue
    else:
        print(f'HC-SR04 Distance: {distance_hc} cm')
    
    percentage = calculate_percentage(distance_aj)
    print(f'Precentage :{percentage}')

    # Control the servo motor based on HC-SR04 distance (lid open/close logic)
    if distance_hc <= 20:
        control_servo("OPEN")  # Open the bin lid if distance <= 20 cm
        binLid_status = "OPEN"
    else:
        control_servo("CLOSED")  # Close the bin lid if distance > 20 cm
        binLid_status = "CLOSED"

    # Check for significant changes in distances to send immediate updates
    if (previous_distance_aj is None or abs(previous_distance_aj - distance_aj) > distance_threshold or
        previous_distance_hc is None or abs(previous_distance_hc - distance_hc) > distance_threshold):

        # Prepare dynamic data to send to the Node.js server
        status_obj = {
            "id": 1,
            "binLocation": "Canteen",
            "distance": distance_aj,
            "filledBinPercentage": percentage,
            "geoLocation": "2d45345345,87768668",
            "microProcessorStatus": "ON",
            "sensorStatus": waste_level_sensor_status,
            "binLidStatus": binLid_status,
            "maxBinCapacity": binMaxCapacity
        }

        try:
            response = urequests.post(nodejs_server_url, json=status_obj)
            print(f'Status update sent: {response.status_code}, Response: {response.text}')
            response.close()
        except Exception as e:
            print('Error sending status update:', e)

        print(status_obj)

        # Update previous distances
        previous_distance_aj = distance_aj
        previous_distance_hc = distance_hc

        # Update the last status update time after sending an immediate update
        last_status_update_time = time.time()

    # Send status update every 10 seconds if no significant change
    current_time = time.time()
    if current_time - last_status_update_time >= status_update_interval:
        # Prepare dynamic data to send to the Node.js server
#         status_obj = {
#             "type": "distance",
#             "id": 1,
#             "binLid_status": binLid_status,
#             "distance": distance_aj,
#             "location": "Canteen",
#             "microProcessor_status": "ON",
#             "sensor_status": waste_level_sensor_status  # Use the updated sensor status
#         }
        status_obj = {
            "id": 1,
            "binLocation": "Canteen",
            "distance": distance_aj,
            "filledBinPercentage": percentage,
            "geoLocation": "2d45345345,87768668",
            "microProcessorStatus": "ON",
            "sensorStatus": waste_level_sensor_status,
            "binLidStatus": binLid_status,
            "maxBinCapacity": binMaxCapacity
        }


        try:
            response = urequests.post(nodejs_server_url, json=status_obj)
            print(f'Status update sent (interval): {response.status_code}, Response: {response.text}')
            response.close()
        except Exception as e:
            print('Error sending status update:', e)

        print(status_obj)

        # Update the last status update time
        last_status_update_time = current_time

    time.sleep(1)  # Check every second for distance changes


