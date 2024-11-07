import RPi.GPIO as GPIO
import time

print("Ultrasonic sensor example, setting pins...")
# Define GPIO pins
URTRIG = 4  # Replace with your trigger pin number
URPWM = 17  # Replace with your PWM (echo) pin number

# Set up GPIO mode
print("Setting up GPIO...")
GPIO.setmode(GPIO.BCM)
GPIO.setup(URTRIG, GPIO.OUT)  # Set trigger pin as output
GPIO.setup(URPWM, GPIO.IN)  # Set echo pin as input
print("GPIO setup complete.")

def ultrasonic_setup():
    # Set up the trigger pin
    GPIO.output(URTRIG, GPIO.HIGH)  # Set trigger to HIGH


def ultrasonic_distance():
    # Trigger the ultrasonic sensor
    print("Triggering ultrasonic sensor...")
    GPIO.output(URTRIG, GPIO.LOW)
    time.sleep(0.000002)  # Short delay (2 microseconds)
    GPIO.output(URTRIG, GPIO.HIGH)
    time.sleep(0.00001)  # Send a 10us pulse to start reading
    GPIO.output(URTRIG, GPIO.LOW)

    # Measure the duration of the pulse
    print("Measuring pulse duration...")
    start_time = time.time()
    print("Waiting for pulse to start...")
    while GPIO.input(URPWM) == GPIO.HIGH:
        start_time = time.time()

    print("Pulse detected, measuring end time...")
    while GPIO.input(URPWM) == GPIO.LOW:
        end_time = time.time()

    # Calculate distance based on the duration of the pulse
    pulse_duration = end_time - start_time
    distance = pulse_duration * 34300 / 2  # speed of sound is 34300 cm/s, divide by 2 for round-trip

    return round(distance, 2)


# Run setup
print("Running ultrasonic setup...")
ultrasonic_setup()
print("Setup complete.")

# Example usage
try:
    while True:
        print("Reading distance...")
        dist = ultrasonic_distance()
        print("Distance:", dist, "cm")
        time.sleep(1)  # Delay between readings
except KeyboardInterrupt:
    print("Got Keyboard interrupt, exiting program.")
    GPIO.cleanup()  # Clean up GPIO on CTRL+C
