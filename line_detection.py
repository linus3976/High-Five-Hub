import cv2
import numpy as np
import os

class LineFollower:
    def __init__(self, motor_control = None):
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

        # Draw contours on the original frame
        im2 = cv2.drawContours(frame.copy(), contours, -1, (0, 255, 0), 3)
        print("Number of contours detected:", len(contours))

        # Keep only the largest contour
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]

        # Initialize centroid variable
        centroid = None
        if len(contours) > 0:
            M = cv2.moments(contours[0])
            if M['m00'] != 0:
                self.cx = int(M['m10'] / M['m00'])
                self.cy = int(M['m01'] / M['m00'])
                print("Centroid of the biggest area: ({}, {})".format(self.cx, self.cy))
                cv2.circle(im2, (self.cx, self.cy), 5, (255, 0, 0), -1)  # Draw centroid
                centroid = (self.cx, self.cy)  # Store centroid coordinates

        # Draw a point at (0, 0) and the center of the frame
        cv2.circle(im2, (0, 0), 5, (0, 0, 255), -1)
        center_x, center_y = w // 2, h // 2
        cv2.circle(im2, (center_x, center_y), 5, (255, 255, 0), -1)

        # Calculate distance if centroid found
        if centroid is not None:
            self.distance = center_x - centroid[0]
            print("Distance from center to centroid: {:.2f}".format(self.distance))
        return im2

    def process_video(self, video_path):
        """Process a video file frame by frame."""
        cap = cv2.VideoCapture(video_path)

        # if not cap.isOpened():
        #     print("Error: Could not open video.")
        #     return

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("End of video stream.")
                break

            output_frame = self.process_frame(frame)
            cv2.imshow("Processed Video", output_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def process_image_file(self, image_path):
        """Process a single image file."""
        frame = cv2.imread(image_path)
        if frame is None:
            print("Error: Could not open image.")
            return

        output_frame = self.process_frame(frame)
        cv2.imshow("Processed Image", output_frame)
        cv2.imwrite("processed_image.png", output_frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def process_input(self, input_path):
        """Process an input file (image or video)."""
        _, ext = os.path.splitext(input_path)
        ext = ext.lower()

        if ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            print("Processing image...")
            self.process_image_file(input_path)
        elif ext in ['.mp4', '.avi', '.mov']:
            print("Processing video...")
            self.process_video(input_path)
        else:
            print("Unsupported file format.")

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


if __name__ == '__main__':
    # Example usage
    input_path = "data/vid1.avi"  # Replace with your image or video file path
    line_follower = LineFollower()
    line_follower.process_input(input_path)
    line_follower.direct_to_line()
