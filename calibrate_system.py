import logging

from car_lib import *
import cv2
import os
from picamera import PiCamera
from picamera.array import PiRGBArray
from croisement import detect_intersections
from time import perf_counter, sleep



def initilize():
    global camera, raw_capture, urkab
    # Initialize the PiCamera
    camera = PiCamera()
    camera.resolution = (160, 128)
    camera.framerate = 32
    raw_capture = PiRGBArray(camera, size=camera.resolution)
    sleep(0.1)  # Allow the camera to warm up

    urkab = Urkab()
    urkab.carResetEmergencyStop()


def calibrate_turning():
    global camera, raw_capture, urkab
    # Initialize variables tracking
    previous_intersection = False
    frames_without_intersection = 0  # Counter for consecutive frames without intersection

    urkab.carTurnRight(250,250)
    start_time = perf_counter()
    lost_intersection = False
    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        image = frame.array  # Get the current frame as an array

        # Check for intersection
        intersection_detected = detect_intersections(image)
        if intersection_detected:
            if not lost_intersection:
                if not previous_intersection: logging.info("Intersection detected!")
                frames_without_intersection = 0  # Reset the no-intersection counter
                previous_intersection = True
            else:
                break
        if (not intersection_detected) and previous_intersection:
            logging.debug("No intersection detected.")
            # If an intersection was previously detected but is now no longer visible
            frames_without_intersection += 1  # Increment the no-intersection counter
            logging.debug(f"Frames without intersection: {frames_without_intersection}")

            # If we have two consecutive frames without detecting an intersection, proceed to the next direction
            if frames_without_intersection >= 2:
                # Lost the intersection
                previous_intersection = False
                lost_intersection = True

            cv2.imshow("Camera feed", image)
        raw_capture.truncate(0)

    end_time = perf_counter()
    urkab.carStop()
    return end_time - start_time

def main():
    global camera, raw_capture, urkab
    try:
        print("HighFive Calibration system: Place Urkab in front of an intersection")
        input("Press enter to start calibration")
        initilize()
        time_to_turn = calibrate_turning()
        print(f"Time to turn: {time_to_turn}")
    except KeyboardInterrupt:
        urkab.carStop()
        camera.close()
        print("Calibration stopped by user")
        exit()
    finally:
        # Release resources and stop the car
        try:
            time_to_turn = time_to_turn * (360/380)

            variable_name = "TIME_TO_TURN"
            variable_value = str(time_to_turn)
            env_file_path = "./turning_const.env"
            with open(env_file_path, "a") as env_file:
                env_file.write(f"{variable_name}={variable_value}\n")

            logging.debug(f"Added {variable_name} to {env_file_path}.")

            cv2.destroyAllWindows()
            urkab.carStop()
            urkab.carDisconnect()
        except serial.serialutil.PortNotOpenError:
            pass

if __name__ == "__main__":
    main()