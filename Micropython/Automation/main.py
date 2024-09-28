import urequests
import machine
import time
import network

# Set up GPIO pins for LEDs
led1 = machine.Pin(26, machine.Pin.OUT)
led2 = machine.Pin(25, machine.Pin.OUT)
led3 = machine.Pin(33, machine.Pin.OUT)
led4 = machine.Pin(32, machine.Pin.OUT)

# Firebase URL
firebase_url = 'https://iwms-automation-default-rtdb.firebaseio.com/Automation.json'


#Old Link: https://iwms-v2-default-rtdb.firebaseio.com/Automation.json
#New Link:https://iwms-automation-default-rtdb.firebaseio.com/Automation.json

# Wi-Fi Credentials
SSID = 'Redmi'  # Replace with your Wi-Fi network name
PASSWORD = '876543210'  # Replace with your Wi-Fi password

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
        response = urequests.get(firebase_url)
        data = response.json()
        response.close()

        if data:
            # Update LEDs based on Firebase data
            led1.value(1 if data['Led-1'] else 0)
            led2.value(1 if data['Led-2'] else 0)
            led3.value(1 if data['Led-3'] else 0)
            led4.value(1 if data['Led-4'] else 0)
    except Exception as e:
        print('Error fetching data:', e)

# Main program execution
def main():
    connect_to_wifi()  # Connect to Wi-Fi first

    # Main loop to fetch LED status from Firebase
    while True:
        get_led_status()
        time.sleep(0.2)  # Wait 2 seconds before the next request

# Run the program
main()
