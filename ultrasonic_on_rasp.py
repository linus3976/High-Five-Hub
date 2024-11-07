import RPi.GPIO as GPIO
import time

# Pin definitions
URTRIG = 4  # Trigger pin (BCM GPIO number, adjust if needed)
URPWM = 17   # Echo pin (BCM GPIO number, adjust if needed)

# Setup function for the ultrasonic sensor
def UltrasonicSetup():
    GPIO.setmode(GPIO.BCM)            # Use BCM GPIO numbering
    GPIO.setup(URTRIG, GPIO.OUT)      # Set trigger pin as output
    GPIO.setup(URPWM, GPIO.IN)        # Set echo pin as input
    GPIO.output(URTRIG, GPIO.HIGH)    # Initially set trigger pin to HIGH

# Function to calculate the distance
def UltrasonicDistance():
    # Trigger the ultrasonic sensor
    GPIO.output(URTRIG, GPIO.LOW)
    time.sleep(0.000002)              # Delay for 2 microseconds
    GPIO.output(URTRIG, GPIO.HIGH)    # Send a short pulse
    time.sleep(0.00001)               # 10 microseconds pulse
    GPIO.output(URTRIG, GPIO.LOW)

    # Wait for the echo to be received
    start_time = time.time()
    while GPIO.input(URPWM) == 0:
        start_time = time.time()      # Record the time of the rising edge

    stop_time = time.time()
    while GPIO.input(URPWM) == 1:
        stop_time = time.time()       # Record the time of the falling edge

    # Calculate the time difference
    elapsed_time = stop_time - start_time
    # Distance calculation: time (in seconds) * speed of sound (34300 cm/s) / 2
    distance = (elapsed_time * 34300) / 2

    return distance

# Example usage
try:
    UltrasonicSetup()
    while True:
        dist = UltrasonicDistance()
        print(f"Distance: {dist:.2f} cm")
        time.sleep(1)  # Wait a second between readings

except KeyboardInterrupt:
    print("Measurement stopped by user")

finally:
    GPIO.cleanup()  # Clean up the GPIO pins
