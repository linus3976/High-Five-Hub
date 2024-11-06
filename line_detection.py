import cv2
import numpy as np
from PID import PIDController

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
        """Process a single frame (image) for line detection and visualization."""
        h, w = frame.shape[:2]
        print("Width, Height:", w, h)

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
        print("Number of contours detected:", len(contours))

        # Keep only the largest contour
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]

        # Initialize centroid variable
        centroid = None
        if len(contours) > 0:
            # Draw the largest contour on the frame
            cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)

            M = cv2.moments(contours[0])
            if M['m00'] != 0:
                self.cx = int(M['m10'] / M['m00'])
                self.cy = int(M['m01'] / M['m00'])
                print("Centroid of the biggest area: ({}, {})".format(self.cx, self.cy))
                centroid = (self.cx, self.cy)

                # Draw the centroid
                cv2.circle(frame, centroid, 5, (255, 0, 0), -1)

        # Draw center line for reference
        center_x = w // 2
        cv2.line(frame, (center_x, 0), (center_x, h), (255, 255, 0), 2)

        # Calculate distance if centroid found
        if centroid is not None:
            self.distance = center_x - centroid[0]
            print("Distance from center to centroid: {:.2f}".format(self.distance))
            # Optionally display distance on the frame
            cv2.putText(frame, f"Dist: {self.distance}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        return frame

    def direct_to_line(self):
        """Direct the vehicle based on line position."""
        threshold = 10  # Small threshold to account for minor deviations
        if abs(self.distance) <= threshold:
            print("Go straight")
            self.motor_control("straight")
        elif self.distance > 0:
            print("Turn left")
            self.motor_control("left")
        else:
            print("Turn right")
            self.motor_control("right")
            
    def apply_control(self, motor_left, motor_right, urkab):
        """Direct the vehicle based on line position."""
        
        threshold = 1.5  # Small threshold to account for minor deviations
        if abs(self.distance) <= threshold:
            print("Go straight")
            self.motor_control("straight")
        else :
            urkab.carAdvance(motor_right, motor_left)
            print("Right: ", motor_right, " Left: ", motor_left)
            
