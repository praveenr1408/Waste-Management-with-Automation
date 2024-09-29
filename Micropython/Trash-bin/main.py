import urequests
import time
import network
from ultrasonic_sensor import UltrasonicSensor
from machine import Pin

LED = Pin(26, Pin.OUT)

# Wi-Fi credentials
ssid = "Redmi"
password = "876543210"

station = network.WLAN(network.STA_IF)
station.active(True)

def connect_wifi(retries=5, delay=5):
    """
    Attempt to connect to Wi-Fi. Retry if connection fails.
    
    :param retries: Maximum number of retries before giving up
    :param delay: Delay between retries in seconds
    """
    attempt = 0
    while not station.isconnected() and attempt < retries:
        try:
            print(f"Attempting to connect to Wi-Fi (Attempt {attempt+1}/{retries})...")
            station.connect(ssid, password)
            time.sleep(delay)
            attempt += 1
        except OSError as e:
            print(f"OSError occurred: {e}")
            time.sleep(delay)  # Wait before retrying

    if station.isconnected():
        print("Connected to Wi-Fi:", station.ifconfig())
        return True
    else:
        print("Failed to connect to Wi-Fi after multiple attempts")
        return False

# Initial connection attempt
connected = connect_wifi()

if not connected:
    # If the initial connection fails, you can choose to halt or retry indefinitely
    while not connected:
        print("Retrying connection in 10 seconds...")
        time.sleep(10)
        connected = connect_wifi()

# Firebase URL
firebase_url = "https://eco-smart-wms-default-rtdb.asia-southeast1.firebasedatabase.app/Trash-Bins/Canteen/Bin-1.json"

# Use GPIO 12 for Trig and GPIO 14 for Echo
sensor = UltrasonicSensor(trig_pin=12, echo_pin=14)

while True:
    # Check Wi-Fi connection, attempt reconnection if necessary
    if not station.isconnected():
        print("Wi-Fi disconnected. Attempting to reconnect...")
        connect_wifi()

    distance = sensor.measure_distance()
    print("Distance:", distance, "cm")
    
    if distance <= 50:
        # set_servo_angle(90)  # Turn servo to 90 degrees
        LED.value(1)
        time.sleep(1)
    else:
        # set_servo_angle(0)
        LED.value(0)

    # Send data to Firebase
    data = {"distance": distance}

    try:
        response = urequests.patch(firebase_url, json=data)
        print(response.text)

        if response.status_code == 200:
            print("Data successfully updated")
        else:
            print(f"Failed to send data, status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending data: {e}")
    
    time.sleep(0.5)  # Send data every 2 seconds
