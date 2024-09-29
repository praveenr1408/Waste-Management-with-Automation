import urequests
import machine
import time
import network

# Firebase Configuration
FIREBASE_URL = 'https://eco-smart-wms-default-rtdb.asia-southeast1.firebasedatabase.app/Automation.json'
FIREBASE_SECRET = 'd3LwMW7cGlDZVAdI6MFaPdQXCNAjuCidyeJJjLQB'  # Replace with your actual Firebase secret key

# Wi-Fi Credentials
SSID = 'Redmi'  # Your Wi-Fi network name
PASSWORD = '876543210'  # Your Wi-Fi password

# Set up GPIO pins for LEDs
led1 = machine.Pin(26, machine.Pin.OUT)
led2 = machine.Pin(25, machine.Pin.OUT)
led3 = machine.Pin(33, machine.Pin.OUT)
led4 = machine.Pin(32, machine.Pin.OUT)

# Function to connect to Wi-Fi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)  # Create a station interface object
    wlan.active(True)  # Activate the station interface
    wlan.connect(SSID, PASSWORD)  # Connect to the Wi-Fi network

    print('Connecting to Wi-Fi...', SSID)
    
    while not wlan.isconnected():  # Wait until connected
        time.sleep(1)
    
    print('Connected to Wi-Fi. Network config:', wlan.ifconfig())

# Function to get LED status from Firebase
def get_led_status():
    try:
        # Append the secret key to the Firebase URL
        response = urequests.get(f"{FIREBASE_URL}?auth={FIREBASE_SECRET}")
        data = response.json()
        response.close()

        if data:
            # Update LEDs based on Firebase data
            led1.value(1 if data.get('Led-1', False) else 0)
            led2.value(1 if data.get('Led-2', False) else 0)
            led3.value(1 if data.get('Led-3', False) else 0)
            led4.value(1 if data.get('Led-4', False) else 0)
    except Exception as e:
        print('Error fetching data:', e)

# Main program execution
def main():
    connect_to_wifi()  # Connect to Wi-Fi first

    # Main loop to fetch LED status from Firebase
    while True:
        get_led_status()
        time.sleep(0.1)  # Wait 2 seconds before the next request

# Run the program
main()
