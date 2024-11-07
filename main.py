import logging
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

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    # Initialize motor controller and line follower with motor control function
    motor_controller = Urkab()
    line_follower = LineFollower(motor_control=motor_control)
    PID_control = PIDController(1.5, 0.4, 1.2, 230, 0) # values: kp, ki, kd, base_speed, setpoint

    previous_time = time.perf_counter()
    delta_time = 0.1

    logging.debug("Initializing Camera...")
    # Initialize the PiCamera
    camera = PiCamera()
    camera.resolution = (160, 128)
    camera.framerate = 32
    raw_capture = PiRGBArray(camera, size=camera.resolution)
    sleep(0.1)  # Allow the camera to warm up
    logging.debug("Initialized Camera")

    try:
        logging.debug("Started try")
        motor_controller.carDeactivateEmergencyStop()
        turning_mode = False
        lost_line = False
        # Capture frames continuously from the camera
        for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
            logging.debug("--------- Got new frame ---------")
            image = frame.array  # Get the current frame as an array

            # Process the frame for line detection
            processed_frame, white_line_detected = line_follower.process_frame(image)

            ultrasonic_distance = motor_controller.getUltrasonicDist()
            logging.info(f"Ultrasonic distance: {ultrasonic_distance}")
            #logging.debug(f"Turning mode: {turning_mode}, Lost line: {lost_line}")


            # if ultrasonic_distance < 20:
            #     turning_mode = True

            # # No line detected and not turning -> stop
            # if not white_line_detected and not turning_mode:
            #     logging.warning("No line detected and no turning mode -> stop the car")
            #     motor_controller.carStop()

            # line lost
            # if turning_mode and not white_line_detected:
            #     logging.debug("Line lost")
            #     lost_line = True

            # Re-found the line
            # if turning_mode and white_line_detected and lost_line:
            #     logging.debug("Re-found the line")
            #     turning_mode = False
            #     lost_line = False

            # if turning_mode:
            #     logging.debug("Turning the car")
            #     motor_controller.carTurnLeft(200, 200)
            #     cv2.imshow("Turning", processed_frame)
            #     raw_capture.truncate(0)
            #     previous_time = time.perf_counter()
            #     continue

            # Direct the robot based on line detection results
            current_time = time.perf_counter()
            delta_time = current_time - previous_time
            previous_time = current_time

            logging.debug("Directing the robot, based on line detection results")
            motor_left, motor_right = PID_control.update(delta_time, line_follower.get_attributes())    #calculates control motor inputs
            line_follower.apply_control(motor_left, motor_right, motor_controller)

            
            #line_follower.direct_to_line()  # Calls motor_control with the appropriate command

            # Display the processed frame for visual feedback
            cv2.imshow("Line Following", processed_frame)

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
