import time
import math
import board
import adafruit_fxos8700
import adafruit_fxas21002c

# Initialize I2C bus and sensors.
i2c = board.I2C()
accel_mag = adafruit_fxos8700.FXOS8700(i2c)
gyro = adafruit_fxas21002c.FXAS21002C(i2c)

# Complementary filter coefficient for overall orientation.
alpha_filter = 0.98

# Variables for complementary filter (orientation estimation)
last_time = time.monotonic()
roll = 0.0
pitch = 0.0
yaw = 0.0

# EMA smoothing factor for the gyroscope’s roll and yaw rates.
ema_alpha = 0.6  # Closer to 1 reacts faster; closer to 0 gives smoother output.
ema_gyro_x = None  # For roll rate (gyro_x)
ema_gyro_z = None  # For yaw rate (gyro_z)
ema_gyro_y = None  # For pitch rate (gyro_y)
# -------------------------------------------------
# Trick Detection Parameters and State Variables
# -------------------------------------------------
# Roll trick detection (Kickflip vs Heelflip)
roll_trick_state = "idle"          # "idle" or "rotating"
roll_trick_integrated = 0.0        # Integrated roll (degrees) during an event
roll_trick_start_threshold = 150.0  # Start event if |roll rate| > this (deg/s)
roll_trick_stop_threshold = 20.0   # Consider event ending if roll rate < this (deg/s)
roll_stop_count = 0                # Count consecutive low-rate samples
roll_stop_count_threshold = 5      # Number of low-rate samples to mark event end
roll_trick_tolerance = 90.0        # Acceptable tolerance for a 360° event
prev_gyro_x_deg = None
# Yaw trick detection (Shuv it variants)
yaw_trick_state = "idle"           # "idle" or "rotating"
yaw_trick_integrated = 0.0         # Integrated yaw (degrees) during an event
yaw_trick_start_threshold = 150.0   # Start event if |yaw rate| > this (deg/s)
yaw_trick_stop_threshold = 20.0    # End event if yaw rate < this (deg/s)
yaw_stop_count = 0                 # Count consecutive low yaw-rate samples
yaw_stop_count_threshold = 5       # Number of low-rate samples to mark event end
yaw_trick_tolerance = 30.0         # Tolerance for detecting 180° or 360° events
# Pitch trick detection 
pitch_trick_state = "idle"           # "idle" or "rotating"
pitch_trick_integrated = 0.0         # Integrated pitch (degrees) during an event
pitch_trick_start_threshold = 150.0   # Start event if |pitch rate| > this (deg/s)
pitch_trick_stop_threshold = 20.0    # End event if pitch rate < this (deg/s)
pitch_stop_count = 0                 # Count consecutive low yaw-rate samples
pitch_stop_count_threshold = 5       # Number of low-rate samples to mark event end
pitch_trick_tolerance = 10.0         # Tolerance for detecting 180° or 360° events
# -------------------------------------------------
# Print control: only output every 0.5 seconds.
last_print_time = time.monotonic()
print_buffer = []  # List to accumulate messages to be printed.

print("Starting sensor loop with EMA smoothing and trick detection...")

while True:
    current_time = time.monotonic()
    dt = current_time - last_time
    last_time = current_time

    # --- Read Gyroscope Data ---
    # Gyroscope outputs angular velocity in radians per second.
    gyro_x, gyro_y, gyro_z = gyro.gyroscope
    # Convert to degrees per second.
    gyro_x_deg = math.degrees(gyro_x)
    gyro_y_deg = math.degrees(gyro_y)
    gyro_z_deg = math.degrees(gyro_z)
    
    if prev_gyro_x_deg is None:
        prev_gyro_x_deg = gyro_x_deg
    # --- Apply EMA to gyro_x (roll rate) ---
    if ema_gyro_x is None:
        ema_gyro_x = gyro_x_deg
    else:
        ema_gyro_x = ema_alpha * gyro_x_deg + (1 - ema_alpha) * ema_gyro_x

    # --- Apply EMA to gyro_z (yaw rate) ---
    if ema_gyro_z is None:
        ema_gyro_z = gyro_z_deg
    else:
        ema_gyro_z = ema_alpha * gyro_z_deg + (1 - ema_alpha) * ema_gyro_z
    # --- Apply EMA to gyro_y (pitch rate) ---
    if ema_gyro_y is None:
        ema_gyro_y = gyro_y_deg
    else:
        ema_gyro_y = ema_alpha * gyro_y_deg + (1 - ema_alpha) * ema_gyro_y


    # --- Read Accelerometer Data ---
    accel_x, accel_y, accel_z = accel_mag.accelerometer
    # Compute roll and pitch from the accelerometer data.
    roll_acc = math.degrees(math.atan2(accel_y, accel_z))
    pitch_acc = math.degrees(math.atan2(-accel_x, math.sqrt(accel_y**2 + accel_z**2)))

    # --- Complementary Filter for Orientation ---
    roll_gyro = roll + gyro_x_deg * dt
    pitch_gyro = pitch + gyro_y_deg * dt
    yaw += gyro_z_deg * dt  # Yaw is tracked solely by integration.

    roll = alpha_filter * roll_gyro + (1 - alpha_filter) * roll_acc
    pitch = alpha_filter * pitch_gyro + (1 - alpha_filter) * pitch_acc
    
    # --- Roll Trick Detection (Kickflip vs Heelflip) ---
    if roll_trick_state == "idle":
        # Start a roll trick event if the smoothed roll rate exceeds threshold.
        if abs(ema_gyro_x) > roll_trick_start_threshold:
            roll_trick_state = "rotating"
            roll_trick_integrated = 0.0
            roll_stop_count = 0
            print_buffer.append("Roll trick event started!")
    elif roll_trick_state == "rotating":
        # Integrate the raw gyro roll rate.
        roll_trick_integrated += ((gyro_x_deg + prev_gyro_x_deg) / 2) * dt
        prev_gyro_x_deg = gyro_x_deg
        # Check if the smoothed roll rate is low.
        if abs(ema_gyro_x) < roll_trick_stop_threshold:
            roll_stop_count += 1
        else:
            roll_stop_count = 0

        # If low rate persists, end the event.
        if roll_stop_count >= roll_stop_count_threshold:
            if abs(abs(roll_trick_integrated) - 360) < roll_trick_tolerance:
                if roll_trick_integrated > 0:
                    print_buffer.append(f"Heelflip detected! (Integrated roll: {roll_trick_integrated:.2f}°)")
                else:
                    print_buffer.append(f"Kickflip detected! (Integrated roll: {roll_trick_integrated:.2f}°)")
            else:
                print_buffer.append(f"Roll trick ended, rotation: {roll_trick_integrated:.2f}°\n")
            roll_trick_state = "idle"

    # --- Yaw Trick Detection (Shuv it variants) ---
    if yaw_trick_state == "idle":
        # Start a yaw event if the smoothed yaw rate exceeds threshold.
        if abs(ema_gyro_z) > yaw_trick_start_threshold:
            yaw_trick_state = "rotating"
            yaw_trick_integrated = 0.0
            yaw_stop_count = 0
            print_buffer.append("Yaw trick event started!\n")
    elif yaw_trick_state == "rotating":
        # Integrate the yaw rate.
        yaw_trick_integrated += gyro_z_deg * dt

        if abs(ema_gyro_z) < yaw_trick_stop_threshold:
            yaw_stop_count += 1
        else:
            yaw_stop_count = 0

        if yaw_stop_count >= yaw_stop_count_threshold:
            abs_yaw = abs(yaw_trick_integrated)
            # Detect a 180° event.
            if abs(abs_yaw - 180) < yaw_trick_tolerance:
                if yaw_trick_integrated > 0:
                    print_buffer.append(f"Front shuv detected (180° yaw, positive). Integrated yaw: {yaw_trick_integrated:.2f}°")
                else:
                    print_buffer.append(f"Shuv it detected (180° yaw, negative). Integrated yaw: {yaw_trick_integrated:.2f}°\n")
            # Detect a 360° event.
            elif abs(abs_yaw - 360) < yaw_trick_tolerance:
                if yaw_trick_integrated > 0:
                    print_buffer.append(f"Front 360 Shuv  detected (yaw positive). Integrated yaw: {yaw_trick_integrated:.2f}°")
                else:
                    print_buffer.append(f"360 Shuv it detected (yaw negative). Integrated yaw: {yaw_trick_integrated:.2f}°")
            else:
                print_buffer.append(f"Yaw trick ended, rotation: {yaw_trick_integrated:.2f}°")
            
            yaw_trick_state = "idle"

    # --- Print Output Every 0.5 Seconds ---

    if (current_time - last_print_time) >= 0.5:
        # Create a combined message with orientation data and any trick messages.
        orientation_msg = f"Orientation -> Roll: {roll:6.2f}°, Pitch: {pitch:6.2f}°, Yaw: {yaw:6.2f}°"
        # Combine the orientation with any trick messages that accumulated.
        if print_buffer:
            combined_msg = orientation_msg + " | " + " | ".join(print_buffer)
        else:
            combined_msg = orientation_msg

        print(combined_msg)
        print_buffer = []  # Clear the buffer.
        last_print_time = current_time

    time.sleep(0.01)

