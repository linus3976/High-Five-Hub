import RPi.GPIO as GPIO
import time

# Define GPIO pins
URTRIG = 4  # Trigger pin number
URPWM = 17  # Echo pin number

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(URTRIG, GPIO.OUT)  # Set trigger pin as output
GPIO.setup(URPWM, GPIO.IN)  # Set echo pin as input

def ultrasonic_setup():
    # Initialize the trigger pin
    GPIO.output(URTRIG, GPIO.HIGH)

def ultrasonic_distance():
    # Trigger the ultrasonic sensor
    GPIO.output(URTRIG, GPIO.LOW)
    time.sleep(0.000002)  # Short delay (2 microseconds)
    GPIO.output(URTRIG, GPIO.HIGH)
    time.sleep(0.00001)  # Send a 10us pulse to start reading
    GPIO.output(URTRIG, GPIO.LOW)

    # Measure the duration of the pulse
    start_time = time.time()
    timeout = start_time + 0.02  # 20ms timeout for waiting on pulse to start

    # Wait for the pulse to start
    while GPIO.input(URPWM) == GPIO.HIGH:
        start_time = time.time()
        if time.time() > timeout:
            print("Timeout: Pulse start not detected.")
            return None  # Timeout condition

    # Measure end time
    end_time = time.time()
    timeout = end_time + 0.02  # 20ms timeout for waiting on pulse to end

    while GPIO.input(URPWM) == GPIO.LOW:
        end_time = time.time()
        if time.time() > timeout:
            print("Timeout: Pulse end not detected.")
            return None  # Timeout condition

    # Calculate distance based on the duration of the pulse
    pulse_duration = end_time - start_time
    distance = pulse_duration * 34300 / 2  # speed of sound is 34300 cm/s, divide by 2 for round-trip

    return round(distance, 2)

# Run setup
ultrasonic_setup()

# Example usage
try:
    while True:
        distance = ultrasonic_distance()
        if distance is not None:
            print("Distance:", distance, "cm")
        else:
            print("Failed to read distance.")
        time.sleep(1)  # Delay between readings
except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO on CTRL+C
