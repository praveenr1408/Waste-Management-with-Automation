import machine
import time
from machine import Pin
import network
import socket
import ujson

# Constants
TRIG_PIN = 12
ECHO_PIN = 14
LED_PIN = 26
DISTANCE_THRESHOLD = 50  # cm
MEASUREMENT_INTERVAL = 5  # seconds
MAX_SOCKET_ATTEMPTS = 5
MAX_DISTANCE_RETRIES = 3
DISTANCE_TIMEOUT = 1000000  # 1 second in microseconds

# Embedded configuration
SSID = 'Redmi'
PASSWORD = '876543210'
SERVER_URL = 'test-iot-554d.onrender.com'
SERVER_PORT = 80  # Change to the correct port if necessary
LOCATION = 'Library'
BIN_ID = 1

# Hardware setup
led = Pin(LED_PIN, Pin.OUT)
trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# Optionally: If you have an IR sensor for the bin lid status
IR_SENSOR_PIN = 27
bin_lid = Pin(IR_SENSOR_PIN, Pin.IN)

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

def measure_distance():
    """Measure distance using the ultrasonic sensor."""
    for _ in range(MAX_DISTANCE_RETRIES):
        trig.value(0)
        time.sleep_us(2)
        trig.value(1)
        time.sleep_us(10)
        trig.value(0)

        start_time = time.ticks_us()

        while echo.value() == 0:
            if time.ticks_diff(time.ticks_us(), start_time) > DISTANCE_TIMEOUT:
                return -1

        pulse_start = time.ticks_us()
        while echo.value() == 1:
            if time.ticks_diff(time.ticks_us(), pulse_start) > DISTANCE_TIMEOUT:
                return -1

        pulse_end = time.ticks_us()
        pulse_duration = time.ticks_diff(pulse_end, pulse_start)
        distance = (pulse_duration * 0.0343) / 2
        return int(distance)

    return -1

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
        distance = measure_distance()
        if distance == -1:
            sensor_status = "OFF"
        else:
            sensor_status = "ON"
            led.value(1 if distance <= DISTANCE_THRESHOLD else 0)

        # Determine bin lid status if you have the IR sensor
        bin_lid_status = "OPEN" if bin_lid.value() == 1 else "CLOSE"

        data = {
            "type": "distance",
            "id": BIN_ID,
            "distance": distance,
            "location": LOCATION,
            "sensor_status": sensor_status,
            "microProcessor_status": "ON",
            "binLid_status": bin_lid_status
        }

        if not send_data(s, data):
            s = connect_socket()  # Reconnect if sending fails

        time.sleep(MEASUREMENT_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        led.value(0)
