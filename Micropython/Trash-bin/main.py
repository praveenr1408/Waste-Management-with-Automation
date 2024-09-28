# main.py
import urequests
import time
import network
from ultrasonic_sensor import UltrasonicSensor

# Connect to Wi-Fi
ssid = "Redmi"
password = "876543210"

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    pass

print("Connected to Wi-Fi")

# Firebase URL (add a unique child key if necessary)
firebase_url = "https://iwms-v2-default-rtdb.firebaseio.com/Trash-Bin.json"

# Use GPIO 12 for Trig and GPIO 14 for Echo
sensor = UltrasonicSensor(trig_pin=12, echo_pin=14)

while True:
    distance = sensor.measure_distance()
    print("Distance:", distance, "cm")

    # Send data to Firebase
    data = {"distance": distance}

    # Use PATCH instead of POST if you want to update a specific node/key
    response = urequests.patch(firebase_url, json=data)
    print(response.text)
    
    # Add some error handling if the request fails
    if response.status_code == 200:
        print("Data successfully updated")
    else:
        print(f"Failed to send data, status code: {response.status_code}")

    time.sleep(0.1)  # Send data every 2 seconds
