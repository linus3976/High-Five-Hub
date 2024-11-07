from picamera.array import PiRGBArray
from picamera import PiCamera
import logging
import time
import numpy as np
import math
import cv2

def detect_intersections(frame, angle_threshold=20, distance_threshold=5):
    logging.debug("Detecting intersections...")
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Threshold the image to isolate white lines
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

    # Edge detection using Canny with lower thresholds
    edges = cv2.Canny(thresh, 30, 100, apertureSize=3)

    # Use Hough Line Transform with adjusted parameters for low resolution
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=20, maxLineGap=5)

    intersections = []  # List to store intersections

    def calculate_angle(line1, line2):
        """Calculate the angle between two lines in degrees."""
        x1, y1, x2, y2 = line1
        x3, y3, x4, y4 = line2
        angle1 = math.atan2(y2 - y1, x2 - x1)
        angle2 = math.atan2(y4 - y3, x4 - x3)
        angle = abs(math.degrees(angle1 - angle2))
        return min(angle, 180 - angle)

    def is_near_point(p1, p2, threshold):
        """Check if two points are within a certain distance."""
        return np.linalg.norm(np.array(p1) - np.array(p2)) < threshold

    if lines is not None:
        # Detect intersections
        for i in range(len(lines)):
            for j in range(i + 1, len(lines)):
                line1 = lines[i][0]
                line2 = lines[j][0]
                x1, y1, x2, y2 = line1
                x3, y3, x4, y4 = line2

                # Calculate the angle between the two lines
                angle = calculate_angle(line1, line2)
                if angle < angle_threshold:  # Skip if angle is too small (lines are nearly parallel)
                    continue

                # Line 1: A1x + B1y + C1 = 0
                A1 = y2 - y1
                B1 = x1 - x2
                C1 = x2 * y1 - x1 * y2

                # Line 2: A2x + B2y + C2 = 0
                A2 = y4 - y3
                B2 = x3 - x4
                C2 = x4 * y3 - x3 * y4

                # Solving the system of equations to find intersection
                denom = A1 * B2 - A2 * B1
                if denom != 0:  # Lines are not parallel
                    intersect_x = (B1 * C2 - B2 * C1) / denom
                    intersect_y = (A2 * C1 - A1 * C2) / denom
                    intersection_point = (int(intersect_x), int(intersect_y))

                    # Check if the intersection point is close to either line's endpoints (noise filtering)
                    if (is_near_point(intersection_point, (x1, y1), distance_threshold) or
                        is_near_point(intersection_point, (x2, y2), distance_threshold) or
                        is_near_point(intersection_point, (x3, y3), distance_threshold) or
                        is_near_point(intersection_point, (x4, y4), distance_threshold)):
                        continue  # Ignore if too close to any endpoint

                    intersections.append(intersection_point)

        # Mark intersections if found
        if intersections:
            for intersection in intersections:
                cv2.circle(frame, intersection, 5, (0, 0, 255), -1)  # Draw red circle at intersections
            logging.info(f'Found intersection')
        else:
            logging.debug("No intersections detected.")

    return intersections


if __name__ == "__main__":
    # Initialize the Raspberry Pi camera
    camera = PiCamera()
    camera.resolution = (160, 128)
    camera.framerate = 32
    raw_capture = PiRGBArray(camera, size=(160, 128))

    # Allow the camera to warm up
    time.sleep(0.1)

    # Capture frames from the Pi camera
    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        # Grab the image array from the frame
        image = frame.array

        # Detect intersections directly on the frame
        intersections = detect_intersections(image)

        # Display the frame with intersections
        cv2.imshow('Intersections', image)

        # Break the loop when 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Clear the stream for the next frame
        raw_capture.truncate(0)

    # Close the display window
    cv2.destroyAllWindows()
