# PID parameters
kp = 1.0  # Proportional gain
ki = 0.1  # Integral gain
kd = 0.05  # Derivative gain
setpoint = 0  # Desired target value

# State variables
previous_error = 0
integral = 0

def pid_update(base_speed, current_value, dt):
    global previous_error, integral
    
    # Calculate the error between the setpoint and the current value
    error = setpoint - current_value
    
    # Proportional term
    p_term = kp * error
    
    # Integral term
    integral += error * dt  # Sum of errors over time
    i_term = ki * integral
    
    # Derivative term
    derivative = (error - previous_error) / dt if dt > 0 else 0  # Change in error
    d_term = kd * derivative
    
    # Update the previous error for the next iteration
    previous_error = error
    
    # Calculate the total control output
    output = p_term + i_term + d_term
    
    left_motor_speed = max(0, min(255, base_speed - output))
    right_motor_speed = max(0, min(255, base_speed + output))
    
    return left_motor_speed, right_motor_speed


