import cv2
import numpy as np
import logging
from PID import PIDController


class LineFollower:
    def __init__(self, motor_control=None):
        self.kernel_erode = np.ones((6, 6), np.uint8)
        self.kernel_dilate = np.ones((4, 4), np.uint8)
        self.cx = 0
        self.cy = 0
        self.distance = 0
        self.obstacle_detected = False
        self.motor_control = motor_control  # Reference to motor control function

    def get_attributes(self):
        """getter to have access to the values"""
        return self.distance

    def process_frame(self, frame):
        """Process a single frame (image) for line detection and obstacle avoidance."""
        h, w = frame.shape[:2]
        logging.debug(f"Width, Height: {w}, {h}")

        # Apply Gaussian blur
        blur = cv2.blur(frame, (5, 5))

        # Convert to binary image
        _, thresh1 = cv2.threshold(blur, 168, 255, cv2.THRESH_BINARY)
        hsv = cv2.cvtColor(thresh1, cv2.COLOR_RGB2HSV)

        # Define range of white color in HSV for line detection
        lower_white = np.array([0, 0, 168])
        upper_white = np.array([172, 111, 255])

        # Threshold the HSV image for line detection
        mask = cv2.inRange(hsv, lower_white, upper_white)

        # Remove noise for line detection
        eroded_mask = cv2.erode(mask, self.kernel_erode, iterations=1)
        dilated_mask = cv2.dilate(eroded_mask, self.kernel_dilate, iterations=1)

        # Detect obstacles (assuming obstacles are a specific color, e.g., red)
        lower_obstacle = np.array([0, 50, 50])
        upper_obstacle = np.array([10, 255, 255])
        obstacle_mask = cv2.inRange(hsv, lower_obstacle, upper_obstacle)
        self.obstacle_detected = cv2.countNonZero(obstacle_mask) > 0

        if self.obstacle_detected:
            logging.info("Obstacle detected! Switching to avoidance mode.")
            return self.drive_around_obstacle()

        # Find contours in line detection mask
        contours, _ = cv2.findContours(dilated_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        logging.debug(f"Number of contours detected: {len(contours)}")

        # Keep only the largest contour
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]

        # Initialize centroid variable
        centroid = None
        if len(contours) > 0:
            M = cv2.moments(contours[0])
            if M['m00'] != 0:
                self.cx = int(M['m10'] / M['m00'])
                self.cy = int(M['m01'] / M['m00'])
                logging.debug("Centroid of the biggest area: ({}, {})".format(self.cx, self.cy))
                centroid = (self.cx, self.cy)

        # Calculate distance if centroid found
        if centroid is not None:
            center_x = w // 2
            self.distance = center_x - centroid[0]
            logging.debug("Distance from center to centroid: {:.2f}".format(self.distance))

        return frame

    def drive_around_obstacle(self):
        """Handles the drive-around logic for obstacle avoidance."""
        # Command the vehicle to drive around the obstacle
        self.motor_control("right")  # Initial right turn to avoid obstacle
        time.sleep(0.5)  # Move forward a bit

        # Continue moving forward while obstacle is detected
        while self.obstacle_detected:
            logging.info("Avoiding obstacle...")
            self.motor_control("straight")
            # Continuously check for obstacles in each frame
            time.sleep(0.2)
            self.obstacle_detected = False  # This line will be replaced with continuous detection logic in main loop

        # Once obstacle is bypassed, resume line following
        logging.info("Obstacle cleared, resuming line following.")
        return None  # Indicate to resume line following

    def direct_to_line(self):
        """Direct the vehicle based on line position."""
        threshold = 10  # Small threshold to account for minor deviations
        if abs(self.distance) <= threshold:
            logging.debug("Go straight")
            self.motor_control("straight")
        elif self.distance > 0:
            logging.debug("Turn left")
            self.motor_control("left")
        else:
            logging.debug("Turn right")
            self.motor_control("right")

    def apply_control(self, motor_left, motor_right, urkab):
        """Direct the vehicle based on line position."""
        threshold = 1.5  # Small threshold to account for minor deviations
        if abs(self.distance) <= threshold:
            logging.debug("Go straight")
            urkab.executeDirection("straight")
        else:
            urkab.carAdvance(motor_right, motor_left)
            logging.debug(f"Applying motor values: Right: {motor_right}, Left: {motor_left}")
