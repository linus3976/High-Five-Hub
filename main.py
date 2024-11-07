import cv2
import time
import logging

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

# Main control loop
if __name__ == '__main__':
    # Initialize motor controller and line follower with motor control function
    logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.DEBUG)
    motor_controller = Urkab()
    line_follower = LineFollower(motor_control=motor_control)
    PID_control = PIDController(3, 0.4, 1.2, 255, 0)  # values: kp, ki, kd, base_speed, setpoint

    previous_time = time.perf_counter()
    delta_time = 0.1
    avoiding_obstacle = False  # State variable to track if in obstacle avoidance mode
    avoidance_start_time = None
    obstacle_avoidance_duration = 1.5  # Duration to avoid the obstacle (seconds)

    # Initialize the PiCamera
    camera = PiCamera()
    camera.resolution = (160, 128)
    camera.framerate = 32
    raw_capture = PiRGBArray(camera, size=camera.resolution)
    sleep(0.1)  # Allow the camera to warm up

    try:
        motor_controller.carDeactivateEmergencyStop()
        # Capture frames continuously from the camera
        for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
            image = frame.array  # Get the current frame as an array

            # Check for obstacle detection and manage avoidance timing
            distance = motor_controller.getUltrasonicDist()
            if distance < 37 and not avoiding_obstacle:
                avoiding_obstacle = True
                avoidance_start_time = time.perf_counter()
                motor_controller.avoid_obstacles()
            elif avoiding_obstacle:
                # If still avoiding, check if the avoidance time has expired
                if (time.perf_counter() - avoidance_start_time) > obstacle_avoidance_duration:
                    avoiding_obstacle = False
                    motor_controller.carAdvance(200, 200)  # Resume moving forward

            # Run line following if not avoiding obstacles
            if not avoiding_obstacle:
                # Process the frame for line detection
                processed_frame = line_follower.process_frame(image)

                # Update the PID control based on line position
                motor_left, motor_right = PID_control.update(delta_time, line_follower.get_attributes())
                line_follower.apply_control(motor_left, motor_right, motor_controller)

                # Display the processed frame for visual feedback
                cv2.imshow("Line Following", processed_frame)

            # Update timing for PID
            current_time = time.perf_counter()
            delta_time = current_time - previous_time
            previous_time = current_time

            # Press 'q' to quit the loop early
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Clear the stream for the next frame
            raw_capture.truncate(0)

    finally:
        # Release resources and stop the car
        cv2.destroyAllWindows()
        motor_controller.carStop()
        motor_controller.carDisconnect()
