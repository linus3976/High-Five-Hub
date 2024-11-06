import cv2
import numpy as np
from PID import PIDController
import logging

class LineFollower:
    def __init__(self, motor_control=None):
        self.kernel_erode = np.ones((6, 6), np.uint8)
        self.kernel_dilate = np.ones((4, 4), np.uint8)
        self.cx = 0
        self.cy = 0
        self.distance = 0
        self.motor_control = motor_control  # Reference to motor control function
        

    def get_attributes(self):
        """getter to have access to the values"""
        return self.distance
    

    def process_frame(self, frame):
        """Process a single frame (image) for line detection."""
        h, w = frame.shape[:2]
        logging.info(f"Width, Height: {w}, {h}")

        # Apply Gaussian blur
        blur = cv2.blur(frame, (5, 5))

        # Convert to binary image
        _, thresh1 = cv2.threshold(blur, 168, 255, cv2.THRESH_BINARY)
        hsv = cv2.cvtColor(thresh1, cv2.COLOR_RGB2HSV)

        # Define range of white color in HSV
        lower_white = np.array([0, 0, 168])
        upper_white = np.array([172, 111, 255])

        # Threshold the HSV image
        mask = cv2.inRange(hsv, lower_white, upper_white)

        # Remove noise
        eroded_mask = cv2.erode(mask, self.kernel_erode, iterations=1)
        dilated_mask = cv2.dilate(eroded_mask, self.kernel_dilate, iterations=1)

        # Find contours
        contours, _ = cv2.findContours(dilated_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        logging.info(f"Number of contours detected: {len(contours)}")

        if len(contours) == 0:
            # no line found
            return None

        # Keep only the largest contour
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]

        # Initialize centroid variable
        centroid = None
        if len(contours) > 0:
            M = cv2.moments(contours[0])
            if M['m00'] != 0:
                self.cx = int(M['m10'] / M['m00'])
                self.cy = int(M['m01'] / M['m00'])
                logging.info("Centroid of the biggest area: ({}, {})".format(self.cx, self.cy))
                centroid = (self.cx, self.cy)

        # Calculate distance if centroid found
        if centroid is not None:
            center_x = w // 2
            self.distance = center_x - centroid[0]
            logging.info("Distance from center to centroid: {:.2f}".format(self.distance))

        return frame

    def direct_to_line(self):
        """Direct the vehicle based on line position."""
        threshold = 10  # Small threshold to account for minor deviations
        if abs(self.distance) <= threshold:
            logging.info("Go straight")
            self.motor_control("straight")
        elif self.distance > 0:
            logging.info("Turn left")
            self.motor_control("left")
        else:
            logging.info("Turn right")
            self.motor_control("right")
            
    def apply_control(self, motor_left, motor_right, urkab):
        """Direct the vehicle based on line position."""
        
        threshold = 1.5  # Small threshold to account for minor deviations
        if abs(self.distance) <= threshold:
            logging.info("Go straight")
            self.motor_control("straight")
        else :
            urkab.carAdvance(motor_right, motor_left)
            logging.info(f"Right: {motor_right}, Left: {motor_left}")
            
