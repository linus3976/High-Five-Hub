import cv2
import numpy as np
import math
import logging


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

def detect_intersections(frame, angle_threshold=20, distance_threshold=10):
    logging.debug("Detecting intersections...")
    # Step 1: Convert the frame to grayscale
    img = frame
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Step 2: Threshold the image to isolate white lines
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Step 3: Edge detection using Canny
    edges = cv2.Canny(thresh, 50, 150, apertureSize=3)

    # Step 4: Use Hough Line Transform to detect lines
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=150, minLineLength=80, maxLineGap=10)

    intersection_found = False  # Variable to track if any intersections are found

    if lines is not None:
        logging.debug(f"Number of lines detected: {len(lines)}")
        # Step 5: Detect intersections
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

                    # Intersection detected, mark it on the image
                    cv2.circle(img, intersection_point, 10, (0, 0, 255), -1)  # Draw red circle
                    intersection_found = True
                    return True

    # Step 6: Save the modified image
    #cv2.imwrite('out_test.png', img)

    # Return True if any intersections were found, otherwise False
    return intersection_found

