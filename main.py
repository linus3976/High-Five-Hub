import argparse
import cv2
import time
import logging

from graphe_go_brrrrr import *
from croisement import detect_intersections  # Import intersection detection function
from line_detection import LineFollower
from car_lib import Urkab
from picamera import PiCamera
from picamera.array import PiRGBArray
from PID import PIDController
from time import sleep

DEBUG = True

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

def parse_arguments():
    """Parse command-line arguments for grid parameters."""
    parser = argparse.ArgumentParser(description="Car navigation parameters")
    parser.add_argument("--size", type=int, required=True, help="Size of the grid (N)")
    parser.add_argument("--start", type=int, nargs=2, required=True, help="Starting coordinates as two integers")
    parser.add_argument("--end", type=int, nargs=2, required=True, help="Ending coordinates as two integers")
    parser.add_argument("--dir_init", type=int, nargs=2, required=True, help="Initial direction as a tuple of two integers")

    args = parser.parse_args()
    return args.size, tuple(args.start), tuple(args.end), tuple(args.dir_init)

if __name__ == '__main__':
    if DEBUG:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
    # Parse arguments from the terminal
    size, start, end, dir_init = parse_arguments()

    # Initialize motor controller and line follower with motor control function
    motor_controller = Urkab()
    line_follower = LineFollower(motor_control=motor_control)
    PID_control = PIDController(3, 0.4, 1.2, 255, 0)  # values: kp, ki, kd, base_speed, setpoint

    previous_time = time.perf_counter()
    delta_time = 0.1

    # Initialize the PiCamera
    camera = PiCamera()
    camera.resolution = (160, 128)
    camera.framerate = 32
    raw_capture = PiRGBArray(camera, size=camera.resolution)
    sleep(0.1)  # Allow the camera to warm up

    # Initialize the itinerary
    g = grid_to_adjacency_matrix(size)
    itin = bfs_with_edges_from_matrix(g, start, end, size)
    dir_l = dir_list(dir_list_absolute(itin), dir_init)

    # Initialize intersection tracking
    intersection_detected = False
    previous_intersection = False
    frames_without_intersection = 0  # Counter for consecutive frames without intersection
    direction_index = 0

    # Set the initial direction
    #NOT SURE IF THIS IS ENOUGH OR NOT!!!
    motor_controller.executeDirection(dir_l[direction_index])

    try:
        motor_controller.carDeactivateEmergencyStop()
        
        # Capture frames continuously from the camera
        for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
            logging.debug("----------Processing frame...----------")
            image = frame.array  # Get the current frame as an array

            intersection_detected = detect_intersections(image)
            # Check for intersection
            if intersection_detected:
                logging.info("Intersection detected!")
                if DEBUG:
                    motor_controller.carStop()
                    sleep(1)  # Pause for 1 second
                frames_without_intersection = 0  # Reset the no-intersection counter
            if (not intersection_detected) and previous_intersection:
                logging.debug("No intersection detected.")
                # If an intersection was previously detected but is now no longer visible
                frames_without_intersection += 1  # Increment the no-intersection counter
                logging.debug(f"Frames without intersection: {frames_without_intersection}")

                # If we have two consecutive frames without detecting an intersection, proceed to the next direction
                if frames_without_intersection >= 2:
                    frames_without_intersection = 0  # Reset the counter
                    direction_index += 1  # Move to the next direction in dir_l
                    logging.info(f"Moving to direction_index {direction_index} in the itinerary.")
                    if DEBUG:
                        motor_controller.carStop()
                        time.sleep(1)
                    motor_controller.executeDirection(dir_l[direction_index])

                    # If we've reached the end of the directions, stop the car
                    if direction_index >= len(dir_l):
                        logging.info("End of itinerary reached. Stopping the car.")
                        motor_controller.carStop()
                        break
                    else:
                        motor_control(dir_l[direction_index])  # Set the new direction
                        logging.info(f"Moving in direction: {dir_l[direction_index]}")

            previous_intersection = intersection_detected

            # Process the frame for line detection
            processed_frame = line_follower.process_frame(image)

            # Direct the robot based on line detection results
            motor_left, motor_right = PID_control.update(delta_time, line_follower.get_attributes())  # calculates control motor inputs
            line_follower.apply_control(motor_left, motor_right, motor_controller)

            current_time = time.perf_counter()
            delta_t = current_time - previous_time
            previous_time = current_time
            
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

