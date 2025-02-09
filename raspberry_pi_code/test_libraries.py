import time
import board
import math
import adafruit_fxos8700
import adafruit_fxas21002c
from i2c import Sensor
# Initialize I2C bus and sensors
i2c = board.I2C()
sensor = Sensor()
# FXOS8700 provides both accelerometer and magnetometer data (we use the accelerometer only)
accel_mag = adafruit_fxos8700.FXOS8700(i2c)
gyro = adafruit_fxas21002c.FXAS21002C(i2c)

# Complementary filter coefficient (tweak between 0 and 1)
alpha = 0.98

# Initialize timers and angles
last_time = time.monotonic()
last_print_time = last_time  # For controlling the print frequency
roll = 0.0   # Rotation around the X-axis (in degrees)
pitch = 0.0  # Rotation around the Y-axis (in degrees)
yaw = 0.0    # Rotation around the Z-axis (in degrees)

print("Tracking orientation with complementary filter...")

while True:
    current_time = time.monotonic()
    dt = current_time - last_time
    last_time = current_time

    # Read gyroscope data (in radians per second)
    gyro_x, gyro_y, gyro_z = gyro.gyroscope

    # Convert gyroscope data to degrees per second
    gyro_x_deg = math.degrees(gyro_x)
    gyro_y_deg = math.degrees(gyro_y)
    gyro_z_deg = math.degrees(gyro_z)

    # Read the accelerometer values (in m/s²)
    accel_x, accel_y, accel_z = accel_mag.accelerometer

    # Calculate the roll and pitch from the accelerometer.
    # Roll: rotation about the X-axis, Pitch: rotation about the Y-axis.
    roll_acc = math.degrees(math.atan2(accel_y, accel_z))
    pitch_acc = math.degrees(math.atan2(-accel_x, math.sqrt(accel_y**2 + accel_z**2)))

    # Integrate gyroscope data
    roll_gyro = roll + gyro_x_deg * dt
    pitch_gyro = pitch + gyro_y_deg * dt
    yaw += gyro_z_deg * dt  # Yaw is solely based on gyroscope integration

    # Apply the complementary filter
    roll = alpha * roll_gyro + (1 - alpha) * roll_acc
    pitch = alpha * pitch_gyro + (1 - alpha) * pitch_acc

    # Print the orientation every 0.5 seconds
    if (current_time - last_print_time) >= 0.5:
        print(f"Roll: {roll:6.2f}°, Pitch: {pitch:6.2f}°, Yaw: {yaw:6.2f}°")
        last_print_time = current_time

    #print(f"Roll: {roll:6.2f}°, Pitch: {pitch:6.2f}°, Yaw: {yaw:6.2f}°")
    # Sleep briefly to maintain a sampling rate of roughly 50 Hz
    time.sleep(0.02)

