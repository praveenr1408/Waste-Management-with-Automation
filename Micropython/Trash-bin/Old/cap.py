from machine import Pin, time_pulse_us
import time

# Pin setup
trigger = Pin(12, Pin.OUT)  # Trig pin
echo = Pin(14, Pin.IN)      # Echo pin
led = Pin(26, Pin.OUT)      # LED pin

# Function to measure distance
def measure_distance():
    # Send a 10us pulse to trigger
    trigger.off()
    time.sleep_us(2)
    trigger.on()
    time.sleep_us(10)
    trigger.off()

    # Measure the duration of the echo pulse
    pulse_duration = time_pulse_us(echo, 1, 30000)  # Max 30ms waiting for echo
    if pulse_duration < 0:
        return None  # If there's an error in measurement

    # Calculate distance (in cm)
    distance = (pulse_duration / 2) / 29.1
    return distance

# Main loop
while True:
    distance = measure_distance()

    if distance is not None:
        print("Distance:", distance, "cm")
        # Turn LED on if the object is closer than 20 cm
        if distance < 30:
            led.on()
            time.sleep(2)
        else:
            led.off()

    time.sleep(0.000001)  # Wait for a second before next measurement
