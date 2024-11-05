from line_detection import LineFollower


if __name__ == '__main__':
    input_path = "data/istockphoto-1219172407-640_adpp_is.mp4"  # Replace with your image or video file path
    line_follower = LineFollower()
    line_follower.process_input(input_path)