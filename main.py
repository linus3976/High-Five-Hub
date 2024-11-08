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

DEBUG = False
USE_ARGS = False
DEACT_EMERGENCY_STOP = False

# Define the motor control function
def motor_control(command):
    """Map LineFollower commands to motor actions."""
    if command == "straight":
        urkab.carAdvance(200, 200)  # Move forward
    elif command == "left":
        urkab.carTurnLeft(150, 150)  # Turn left
    elif command == "right":
        urkab.carTurnRight(150, 150)  # Turn right
    else:
        urkab.carStop()  # Stop if no command

def parse_arguments():
    """Parse command-line arguments for grid parameters."""
    parser = argparse.ArgumentParser(description="Car navigation parameters")
    parser.add_argument("--size", type=int, required=True, help="Size of the grid (N)")
    parser.add_argument("--start", type=int, nargs=2, required=True, help="Starting coordinates as two integers")
    parser.add_argument("--end", type=int, nargs=2, required=True, help="Ending coordinates as two integers")
    parser.add_argument("--dir_init", type=int, nargs=2, required=True, help="Initial direction as a tuple of two integers")

    args = parser.parse_args()
    return args.size, tuple(args.start), tuple(args.end), tuple(args.dir_init)


# getting th initial input
def get_user_input():
    """Prompt the user for grid parameters."""
    size = int(input("Enter the size of the grid (N): "))

    start_x = float(input("Enter the starting X coordinate: "))
    start_y = float(input("Enter the starting Y coordinate: "))
    start = (start_x, start_y)

    end_x = float(input("Enter the ending X coordinate: "))
    end_y = float(input("Enter the ending Y coordinate: "))
    end = (end_x, end_y)

    dir_init_x = int(input("Enter the initial direction X component: "))
    dir_init_y = int(input("Enter the initial direction Y component: "))
    dir_init = (dir_init_x, dir_init_y)

    return size, start, end, dir_init

#getting the input if the user wants to ga again
def prompt_user_again():
    if bool(input("Do you want to go somewhere else? [True/False]")):
        end_x = float(input("Enter the ending X coordinates: "))
        end_y = float(input("Enter the ending Y coordinates: "))
        end = end_x, end_y
        return True, end
    else:
        return False, (0.0,0.0)

def initialize():
    if DEBUG:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
    if USE_ARGS:
        # Parse arguments from the terminal
        size, start, end, dir_init = parse_arguments()
    else:
        size, start, end, dir_init = get_user_input()
    # Initialize motor controller and line follower with motor control function
    urkab = Urkab()
    if DEACT_EMERGENCY_STOP:
        urkab.carDeactivateEmergencyStop()
    else:
        urkab.carResetEmergencyStop()
    line_follower = LineFollower(motor_control=motor_control)
    PID_control = PIDController(3, 0.4, 1.2, 255, 0)  # values: kp, ki, kd, base_speed, setpoint

    return size, start, end, dir_init, urkab, line_follower, PID_control

def go_somewhere(size, start, end, dir_init, urkab, line_follower, PID_control):
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
    logging.info(f"Initial itinerary: {dir_l}")

    # Initialize intersection tracking
    intersection_detected = False
    previous_intersection = False
    frames_without_intersection = 0  # Counter for consecutive frames without intersection
    direction_index = 0

    # Set the initial direction
    logging.debug(f"Starting initial positioning, direction is: {dir_l[direction_index]}")
    urkab.executeDirection(dir_l[direction_index])
    logging.debug(f"Should have oriented now... Amen.")

    try:

        # Capture frames continuously from the camera
        for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
            logging.debug("----------Processing frame...----------")
            image = frame.array  # Get the current frame as an array

            intersection_detected = detect_intersections(image)
            # Check for intersection
            if intersection_detected:
                if not previous_intersection: logging.info("Intersection detected!")
                if DEBUG:
                    urkab.carStop()
                    sleep(0.5)  # Pause for 1 second
                frames_without_intersection = 0  # Reset the no-intersection counter
                previous_intersection = True
            if (not intersection_detected) and previous_intersection:
                logging.debug("No intersection detected.")
                # If an intersection was previously detected but is now no longer visible
                frames_without_intersection += 1  # Increment the no-intersection counter
                logging.debug(f"Frames without intersection: {frames_without_intersection}")

                # If we have two consecutive frames without detecting an intersection, proceed to the next direction
                if frames_without_intersection >= 2:
                    previous_intersection = False
                    frames_without_intersection = 0  # Reset the counter
                    direction_index += 1  # Move to the next direction in dir_l
                    logging.info(f"Moving to direction_index {direction_index} in the itinerary.")
                    if DEBUG:
                        urkab.carStop()
                        time.sleep(1)

                    # If we've reached the end of the directions, stop the car
                    if direction_index >= len(dir_l):
                        logging.info("End of itinerary reached. Stopping the car.")
                        urkab.carStop()
                        break
                    else:
                        urkab.executeDirection(dir_l[direction_index])
                        logging.info(f"Moving in direction: {dir_l[direction_index]}")

            # Process the frame for line detection
            processed_frame = line_follower.process_frame(image)

            # Direct the robot based on line detection results
            motor_left, motor_right = PID_control.update(delta_time,
                                                         line_follower.get_attributes())  # calculates control motor inputs
            line_follower.apply_control(motor_left, motor_right, urkab)

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
        current_dir =



if __name__ == '__main__':
    try:
        size, start, end, dir_init, urkab, line_follower, PID_control = initialize()
        go_somewhere(size, start, end, dir_init, urkab, line_follower, PID_control)
        while True:

    except KeyboardInterrupt:
        urkab.carStop()
        urkab.carDisconnect()
        cv2.destroyAllWindows()
        logging.info("Program terminated by user.")