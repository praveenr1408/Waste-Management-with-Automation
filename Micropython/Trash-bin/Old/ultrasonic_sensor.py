from machine import Pin
import time

class UltrasonicSensor:
    def __init__(self, trig_pin, echo_pin):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)

    def measure_distance(self):
        # Send 10us pulse to trigger the sensor
        self.trig.off()
        time.sleep_us(2)
        self.trig.on()
        time.sleep_us(10)
        self.trig.off()

        # Measure the duration of the echo pulse
        while self.echo.value() == 0:
            pass
        start = time.ticks_us()

        while self.echo.value() == 1:
            pass
        end = time.ticks_us()

        # Calculate the distance (duration / 2 * speed of sound)
        duration = time.ticks_diff(end, start)
        #distance = (duration / 2) * 0.0343  # speed of sound in cm/us
        distance = duration * 0.034 / 2

        # Round the distance to a whole number or a specified decimal place
        return int(distance)  # Adjust to 2 decimal places

