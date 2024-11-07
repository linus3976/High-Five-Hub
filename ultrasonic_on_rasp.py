import RPi.GPIO as GPIO
import time

# Pin definitions (adjust these to match your wiring)
URTRIG = 4  # Trigger pin (BCM GPIO number, adjust if needed)
URPWM = 17   # Echo pin (BCM GPIO number, adjust if needed)

# Setup function for the ultrasonic sensor
def UltrasonicSetup():
    GPIO.setmode(GPIO.BCM)            # Use BCM GPIO numbering
    GPIO.setup(URTRIG, GPIO.OUT)      # Set trigger pin as output
    GPIO.setup(URPWM, GPIO.IN)        # Set echo pin as input
    GPIO.output(URTRIG, GPIO.LOW)     # Initialize trigger to LOW

# Function to calculate the distance
def UltrasonicDistance():
    # Trigger the ultrasonic sensor
    GPIO.output(URTRIG, GPIO.LOW)
    time.sleep(0.000002)              # Delay for 2 microseconds
    GPIO.output(URTRIG, GPIO.HIGH)    # Send a short pulse
    time.sleep(0.00001)               # 10 microseconds pulse
    GPIO.output(URTRIG, GPIO.LOW)

    # Measure the pulse width
    start_time = time.time()
    timeout = start_time + 0.02       # Timeout after 20 milliseconds

    # Wait for the pulse to start (Echo goes HIGH)
    while GPIO.input(URPWM) == 0:
        start_time = time.time()
        if start_time > timeout:
            print("Timeout: No pulse detected, possibly out of range.")
            return None  # Timeout occurred, no pulse detected

    # Wait for the pulse to end (Echo goes LOW)
    stop_time = time.time()
    while GPIO.input(URPWM) == 1:
        stop_time = time.time()
        if stop_time > timeout:
            print("Timeout: Pulse did not return within expected range.")
            return None  # Timeout occurred, no pulse detected

    # Calculate distance
    elapsed_time = stop_time - start_time
    distance = (elapsed_time * 34300) / 2  # Convert to cm

    # Debugging information
    print(f"Start time: {start_time}, Stop time: {stop_time}, Elapsed time: {elapsed_time}")
    return distance

# Main loop to run the sensor readings
try:
    UltrasonicSetup()
    while True:
        dist = UltrasonicDistance()
        if dist is None:
            print("No valid distance reading (timeout or out of range)")
        else:
            print(f"Distance: {dist:.2f} cm")
        time.sleep(1)  # Wait a second between readings to allow reliable timing

except KeyboardInterrupt:
    print("Measurement stopped by user")

finally:
    GPIO.cleanup()  # Clean up the GPIO pins
