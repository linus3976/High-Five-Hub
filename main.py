import cv2
import time

from line_detection import LineFollower
from car_lib import Urkab
from picamera import PiCamera
from picamera.array import PiRGBArray
from PID import PIDController

from time import sleep

# Define the motor control function
def motor_control(command):
    """Map LineFollower commands to motor actions."""
    if command == "straight":
        motor_controller.carAdvance(200, 200)  # Move forward
    elif command == "left":
        motor_controller.carTurnLeft(150, 150)  # Turn left
    elif command == "right":
        motor_controller.carTurnRight(150, 150)  # Turn right
    else:
        motor_controller.carStop()  # Stop if no command


# Main loop update to handle obstacle avoidance and line-following
if __name__ == '__main__':
    motor_controller = Urkab()
    line_follower = LineFollower(motor_control=motor_control)

    camera = PiCamera()
    camera.resolution = (160, 128)
    camera.framerate = 32
    raw_capture = PiRGBArray(camera, size=camera.resolution)
    sleep(0.1)

    try:
        motor_controller.carDeactivateEmergencyStop()

        while True:
            # Capture frame for line-following
            for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
                image = frame.array
                processed_frame = line_follower.process_frame(image)

                # Check distance to obstacle
                dist = motor_controller.getUltrasonicDist()
                print(f"Distance to obstacle: {dist}")

                if dist < 15 and dist not in [4, 3]:  # If obstacle is close
                    print("Obstacle detected. Avoiding...")
                    motor_controller.avoid_obstacle_right()  # Avoid obstacle to the right
                else:
                    # Regular line-following when no obstacle is detected
                    line_follower.direct_to_line()

                # Show processed image with detected line
                cv2.imshow("Line Following", processed_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                raw_capture.truncate(0)

    finally:
        cv2.destroyAllWindows()
        motor_controller.carStop()
        motor_controller.carDisconnect()