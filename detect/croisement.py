import cv2
import numpy as np

expected_corners = 3
def_file = ""


def detect_cor(filename=def_file, nb_corners=expected_corners):
    img = cv2.imread(filename)
    blur = cv2.blur(img, (6, 6))
    ret, thresh1 = cv2.threshold(blur, 168, 255, cv2.THRESH_BINARY)
    hsv = cv2.cvtColor(thresh1, cv2.COLOR_RGB2HSV)

    # Define range of white color in HSV
    lower_white = np.array([0, 0, 168])
    upper_white = np.array([172, 111, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)

    kernel_erode = np.ones((6, 6), np.uint8)
    eroded_mask = cv2.erode(mask, kernel_erode, iterations=1)
    kernel_dilate = np.ones((4, 4), np.uint8)
    dilated_mask = cv2.dilate(eroded_mask, kernel_dilate, iterations=1)
    gray = np.float32(dilated_mask)

    dst = cv2.cornerHarris(gray, 5, 3, 0.10)
    corners = cv2.goodFeaturesToTrack(gray, 5, 0.5, 20)
    corners = np.int0(corners) if corners is not None else []

    if len(corners) >= nb_corners:
        return True
    for i in corners:
        x, y = i.ravel()
        print(x, y)
        cv2.circle(img, (x, y), 3, 255, -1)

    # Result is dilated for marking the corners, not important
    dst = cv2.dilate(dst, None)
    cv2.imwrite('out_test.png', img)
    img[dst > 0.02 * dst.max()] = [0, 0, 255]


if __name__ == "__main__":
    # Video processing code
    cap = cv2.VideoCapture('IMG_1726.MOV')  # Replace with 0 for webcam
    frame_skip = 2  # Skip every 2 frames (adjust for desired speed)

    while cap.isOpened():
        for _ in range(frame_skip):  # Skip frames
            ret, frame = cap.read()
            if not ret:
                break

        # Save frame to temporary file to use the existing function
        cv2.imwrite("temp_frame.png", frame)

        # Run corner detection on the current frame
        success = detect_cor("temp_frame.png", expected_corners)

        if success:
            print("Corners detected!")

        # Display the frame
        cv2.imshow("Corners Detection", frame)

        # Press 'q' to quit; reduce waitKey delay to speed up playback
        if cv2.waitKey(10) & 0xFF == ord('q'):  # Reduced delay for faster playback
            break

    cap.release()
    cv2.destroyAllWindows()
