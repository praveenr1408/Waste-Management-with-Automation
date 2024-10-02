import machine
import time
from machine import Pin
import network
import socket
import ujson

# Constants
MEASUREMENT_INTERVAL = 5  # seconds
MAX_SOCKET_ATTEMPTS = 5

# Embedded configuration
SSID = 'Redmi'
PASSWORD = '876543210'
SERVER_URL = 'test-iot-554d.onrender.com'
SERVER_PORT = 80  # Change to the correct port if necessary
LOCATION = 'Library'
BIN_ID = 1

def connect_wifi():
    """Connect to the Wi-Fi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        print('Connecting to Wi-Fi...')
        time.sleep(1)
    print('Connected to Wi-Fi:', wlan.ifconfig())

def ensure_wifi_connected():
    """Ensure Wi-Fi connection is stable."""
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print('Wi-Fi disconnected. Reconnecting...')
        connect_wifi()

def connect_socket():
    """Attempt to connect to the TCP socket server."""
    for attempt in range(MAX_SOCKET_ATTEMPTS):
        try:
            addr_info = socket.getaddrinfo(SERVER_URL, SERVER_PORT)
            addr = addr_info[0][-1]  # Get the socket address from the first tuple
            s = socket.socket()
            s.connect(addr)
            print('Connected to socket server')
            return s
        except Exception as e:
            wait_time = 2 ** attempt
            print(f'Socket connection failed: {e}. Retrying in {wait_time} seconds...')
            time.sleep(wait_time)
    return None

def send_data(s, data):
    """Send data via TCP socket."""
    try:
        if s:
            request = ujson.dumps(data) + "\r\n"  # Append a newline for better handling on the server side
            print("JSON to send:", request)  # Debug: print JSON before sending
            s.send(request.encode('utf-8'))
            print("Data sent:", data)
            response = s.recv(1024)  # Receive server response
            print("Server response:", response.decode('utf-8'))
            return True
    except Exception as e:
        print(f"Error sending data: {e}")
    return False

def main():
    connect_wifi()
    s = connect_socket()

    while True:
        ensure_wifi_connected()

        # Prepare data for sending
        data = {
            "id": BIN_ID,
            "type": "distance",
            "location": LOCATION,
            "microProcessor_status": "ON"
        }

        # Send data to the server
        if not send_data(s, data):
            s = connect_socket()  # Reconnect if sending fails

        time.sleep(MEASUREMENT_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program stopped by user.")
