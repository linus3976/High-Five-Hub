import zmq
import time

# Server IP configuration
server_ip = "192.168.137.1"
command_port = 5005  # Port used to communicate with the server


# Initialize a connection to the server
def connect_to_server(ip, port):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    address = f"tcp://{ip}:{port}"
    socket.connect(address)
    return socket


# Request the latest command from the server
def request_command(socket):
    # Ask the server for the latest command
    request_msg = {"from": "robot", "cmd": "key"}
    socket.send_pyobj(request_msg)

    # Receive the response from the server
    response = socket.recv_pyobj()
    return response.get("key", None)


# Function to execute received commands
def execute_command(command):
    if command == 'w':
        print("Moving forward")
        # Implement the motor control code here to move forward
    elif command == 's':
        print("Moving backward")
        # Implement motor control for moving backward
    elif command == 'a':
        print("Turning left")
        # Implement motor control for turning left
    elif command == 'd':
        print("Turning right")
        # Implement motor control for turning right
    else:
        print("No action or unknown command")


# Main function to connect and run the robot
def main():
    # Connect to the server
    server_socket = connect_to_server(server_ip, command_port)
    print("Connected to server")

    while True:
        # Request the latest command from the server
        command = request_command(server_socket)

        if command:
            print(f"Received command: {command}")
            # Execute the command if valid
            execute_command(command)
        else:
            print("No new command received")

        # Wait a short time before requesting again
        time.sleep(0.1)  # Adjust based on your system needs


if __name__ == "__main__":
    main()
