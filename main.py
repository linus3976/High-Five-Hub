import time
from motor_cmds import arduino, TestMoteur, carAdvance, carBack, carTurnLeft, carTurnRight, resetENC, carStop

def main():
    # Ensure the Arduino is connected
    print("Starting vehicle control...")

    # Example commands to test vehicle functions
    TestMoteur()

    # Move the vehicle forward for 2 seconds
    print("Moving forward...")
    carAdvance(150, 150)
    time.sleep(2)
    carStop()

    # Move the vehicle backward for 2 seconds
    print("Moving backward...")
    carBack(150, 150)
    time.sleep(2)
    carStop()

    # Turn left for 1 second
    print("Turning left...")
    carTurnLeft(150, 150)
    time.sleep(1)
    carStop()

    # Turn right for 1 second
    print("Turning right...")
    carTurnRight(150, 150)
    time.sleep(1)
    carStop()

    # Reset encoders
    print("Resetting encoders...")
    resetENC()

    # Close the Arduino connection
    arduino.write(b'a')  # Disconnect
    arduino.close()
    print("Vehicle control finished.")

if __name__ == "__main__":
    main()
