import network
import websocket
import ujson
import time

# Constants
SSID = 'Redmi'
PASSWORD = '876543210'
SERVER_URL = 'ws://test-iot-554d.onrender.com'  # Replace with your WebSocket server URL

def connect_wifi():
    """Connect to the Wi-Fi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    # Wait for connection
    while not wlan.isconnected():
        print('Connecting to Wi-Fi...')
        time.sleep(1)
    print('Connected to Wi-Fi:', wlan.ifconfig())

def main():
    connect_wifi()
    
    # Connect to WebSocket server
    try:
        ws = websocket.websocket(SERVER_URL)
        
        # Prepare your data
        data = {
            "id": 1,
            "type": "status_update",
            "location": "Library",
            "microProcessor_status": "ON",
        }
        
        # Send data
        ws.send(ujson.dumps(data))
        print("Message sent:", data)

        # Wait for server response
        response = ws.recv()
        print("Server response:", response)

    except Exception as e:
        print("Error:", e)

    finally:
        ws.close()

if __name__ == "__main__":
    main()