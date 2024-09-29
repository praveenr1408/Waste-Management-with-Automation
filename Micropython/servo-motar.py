from machine import Pin, PWM
import time

# Ultrasonic sensor setup
trigger = Pin(14, Pin.OUT)
echo = Pin(27, Pin.IN)

# Servo motor setup (on GPIO 15)
servo = PWM(Pin(15), freq=50)

# Function to set the servo position
def set_servo_angle(angle):
    duty = int(40 + (angle / 180) * 115)  # Convert angle to duty cycle
    servo.duty(duty)

# Function to measure distance using the ultrasonic sensor
def get_distance():
    # Send a pulse
    trigger.value(0)
    time.sleep_us(2)
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)
    
    # Measure the duration of the echo pulse
    while echo.value() == 0:
        pass
    start_time = time.ticks_us()
    
    while echo.value() == 1:
        pass
    end_time = time.ticks_us()
    
    duration = time.ticks_diff(end_time, start_time)
    
    # Calculate distance in cm
    distance = (duration / 2) / 29.1
    return distance

# Main loop to control the servo based on distance
while True:
    distance = get_distance()
    print("Distance:", distance, "cm")
    
    if distance <= 10:
        set_servo_angle(90)  # Turn servo to 90 degrees
    else:
        set_servo_angle(0)   # Turn servo to 0 degrees
    
    time.sleep(1)
