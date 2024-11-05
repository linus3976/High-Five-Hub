import cv2
from line_detection import LineFollower
from motor_cmds import Urkab


# Define the motor control function
def motor_control(command):
    """Map LineFollower commands to motor actions."""
    if command == "straight":
        motor_controller.carAdvance(150, 150)  # Move forward
    elif command == "left":
        motor_controller.carTurnLeft(100, 80)  # Turn left
    elif command == "right":
        motor_controller.carTurnRight(80, 100)  # Turn right
    else:
        motor_controller.carStop()  # Stop if no command


if __name__ == '__main__':
    # Initialize motor controller and line follower with motor control function
    motor_controller = Urkab()
    line_follower = LineFollower(motor_control=motor_control)

    # Replace 'input_path' with your video file path
    input_path = "data/vid1.avi"
    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        print(f"Error: Could not open video file: {input_path}")
        exit()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("End of video stream or error reading frame.")
                break

            # Process the frame for line detection
            processed_frame = line_follower.process_frame(frame)

            # Direct the robot based on line detection results
            line_follower.direct_to_line()  # Calls motor_control with the appropriate command

            # Display the processed frame for visual feedback
            cv2.imshow("Line Following", processed_frame)

            # Press 'q' to quit the loop early
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Release resources and stop the car
        cap.release()
        cv2.destroyAllWindows()
        motor_controller.carStop()
        motor_controller.carDisconnect()
