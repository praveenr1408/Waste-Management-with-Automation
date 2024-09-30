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

def connect_wifi(delay=5):
    """
    Attempt to connect to Wi-Fi. Retry indefinitely if connection fails.
    
    :param delay: Delay between retries in seconds
    """
    while not station.isconnected():
        try:
            print("Attempting to connect to Wi-Fi...")
            station.connect(ssid, password)
            time.sleep(delay)
        except OSError as e:
            print(f"OSError occurred: {e}")
            time.sleep(delay)  # Wait before retrying

    print("Connected to Wi-Fi:", station.ifconfig())

# Initial connection attempt
connect_wifi()

# Firebase URL and Secret
firebase_url = "https://eco-smart-wms-default-rtdb.asia-southeast1.firebasedatabase.app/Trash-Bins/Canteen/Bin-1.json"
firebase_secret = "d3LwMW7cGlDZVAdI6MFaPdQXCNAjuCidyeJJjLQB"  # Replace with your Firebase Database secret

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
        LED.value(1)  # Turn on LED if the distance is less than or equal to 50 cm
        time.sleep(1)
    else:
        LED.value(0)  # Turn off LED otherwise

    # Send data to Firebase
    data = {"distance": distance}
    firebase_url_with_auth = f"{firebase_url}?auth={firebase_secret}"

    try:
        response = urequests.patch(firebase_url_with_auth, json=data)
        print(response.text)

        if response.status_code == 200:
            print("Data successfully updated")
        else:
            print(f"Failed to send data, status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending data: {e}")
    
    time.sleep(2)  # Send data every 2 seconds

