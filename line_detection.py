import cv2
import numpy as np
import os


def process_frame(frame):
    """Process a single frame (image) for line detection."""
    h, w = frame.shape[:2]
    print("Width, Height:", w, h)

    # Apply Gaussian blur
    blur = cv2.blur(frame, (5, 5))

    # Convert to binary image
    ret, thresh1 = cv2.threshold(blur, 168, 255, cv2.THRESH_BINARY)
    hsv = cv2.cvtColor(thresh1, cv2.COLOR_RGB2HSV)

    # Define range of white color in HSV
    lower_white = np.array([0, 0, 168])
    upper_white = np.array([172, 111, 255])

    # Threshold the HSV image
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # Remove noise
    kernel_erode = np.ones((6, 6), np.uint8)
    eroded_mask = cv2.erode(mask, kernel_erode, iterations=1)

    kernel_dilate = np.ones((4, 4), np.uint8)
    dilated_mask = cv2.dilate(eroded_mask, kernel_dilate, iterations=1)

    # Find contours
    contours, hierarchy = cv2.findContours(dilated_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours on the original frame
    im2 = cv2.drawContours(frame.copy(), contours, -1, (0, 255, 0), 3)

    print("Number of contours detected:", len(contours))
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]  # Keep the largest contour only

    centroid = None  # Initialize centroid variable
    if len(contours) > 0:
        M = cv2.moments(contours[0])
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            print("Centroid of the biggest area: ({}, {})".format(cx, cy))
            cv2.circle(im2, (cx, cy), 5, (255, 0, 0), -1)  # Draw centroid
            centroid = (cx, cy)  # Store centroid coordinates
        else:
            print("No centroid found.")
    else:
        print("No contours found.")

    # Draw a point at coordinates (0, 0)
    cv2.circle(im2, (0, 0), 5, (0, 0, 255), -1)  # Draw point at (0, 0) in red

    # Draw a point in the middle of the frame
    center_x = w // 2  # X-coordinate of the center
    center_y = h // 2  # Y-coordinate of the center
    cv2.circle(im2, (center_x, center_y), 5, (255, 255, 0), -1)  # Draw center point in green

    # Calculate distance if the centroid was found
    if centroid is not None:
        distance = (center_x - centroid[0])
        print("Distance from center to centroid: {:.2f}".format(distance))
########### IF THE VALUE IS NEGATIVE -> TURN RIGHT, POSITIV -> TURN LEFT
    return im2


def process_video(video_path):
    """Process a video file frame by frame."""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("End of video stream.")
            break

        output_frame = process_frame(frame)
        cv2.imshow("Processed Video", output_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def process_image_file(image_path):
    """Process a single image file."""
    frame = cv2.imread(image_path)
    if frame is None:
        print("Error: Could not open image.")
        return

    output_frame = process_frame(frame)
    cv2.imshow("Processed Image", output_frame)
    cv2.imwrite("processed_image.png", output_frame)  # Save processed image
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main(input_path):
    """Main function to distinguish between image and video input."""
    _, ext = os.path.splitext(input_path)
    ext = ext.lower()

    if ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        print("Processing image...")
        process_image_file(input_path)
    elif ext in ['.mp4', '.avi', '.mov']:
        print("Processing video...")
        process_video(input_path)
    else:
        print("Unsupported file format.")

if __name__ == '__main__':
    # Example usage
    input_path = "data/istockphoto-1219172407-640_adpp_is.mp4"  # Replace with your image or video file path
    main(input_path)
