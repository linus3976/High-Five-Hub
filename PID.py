import time

class PIDController:
    def __init__(self, kp, ki, kd, base_speed, setpoint=0):
        # PID parameters
        self.kp = kp  # Proportional gain
        self.ki = ki  # Integral gain
        self.kd = kd  # Derivative gain
        self.base_speed = base_speed
        self.setpoint = setpoint  # Desired target value
        
        # State variables
        self.previous_error = 0
        self.integral = 0


    def update(self, dt, current_value):
        """
        Calculate the control output for adjusting motor speeds.
        
        :param base_speed: Base speed for the motors when the car is on the line.
        :param current_value: Current measured value (e.g., distance from the line).
        :param dt: Time difference between measurements (in seconds).
        :return: Tuple (left_motor_speed, right_motor_speed)
        """
        # Calculate the error between the setpoint and the current value
        error = self.setpoint - current_value
        
        # Proportional term
        p_term = self.kp * error
        
        # Integral term
        self.integral += error * dt  # Sum of errors over time
        i_term = self.ki * self.integral
        
        # Derivative term
        derivative = (error - self.previous_error) / dt if dt > 0 else 0  # Change in error
        d_term = self.kd * derivative
        
        # Update the previous error for the next iteration
        self.previous_error = error
        
        # Calculate the total control output
        output = p_term + i_term + d_term
        
        # Calculate motor speeds with output adjustment
        left_motor_speed = int(max(0, min(255, self.base_speed + output)))
        right_motor_speed = int(max(0, min(255, self.base_speed - output)))

        return left_motor_speed, right_motor_speed


