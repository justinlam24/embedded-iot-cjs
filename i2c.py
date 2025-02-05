import time
import smbus2

# I2C Addresses
FXOS8700_ADDR = 0x1F  # Accelerometer + Magnetometer
FXAS21002_ADDR = 0x21  # Gyroscope

# I2C Bus
bus = smbus2.SMBus(1)

def init_fxos8700():
    """ Initialize the FXOS8700 accelerometer """
    # Set device to active mode
    try:
        bus.write_byte_data(FXOS8700_ADDR, 0x2A, 0x01)
        print("I2C write successful!")
    except OSError as e:
        print(f"I2C write failed: {e}")

def read_acceleration():
    """ Read 6 bytes of acceleration data from FXOS8700 """
    accel_data = bus.read_i2c_block_data(FXOS8700_ADDR, 0x01, 6)

    # Convert raw data to signed 14-bit values, since I2C transfers data in 8-bit bytes
    x = (accel_data[0] << 8 | accel_data[1]) >> 2
    y = (accel_data[2] << 8 | accel_data[3]) >> 2
    z = (accel_data[4] << 8 | accel_data[5]) >> 2

    # Convert to G-force (assuming ±2g range, 8192 counts per g)
    x_g = x / 4096.0
    y_g = y / 4096.0
    z_g = z / 4096.0

    return x_g, y_g, z_g

def init_fxas21002():
    """ Initialize the FXAS21002 gyroscope """
    bus.write_byte_data(FXAS21002_ADDR, 0x13, 0x00)  # CTRL_REG1: Standby mode
    bus.write_byte_data(FXAS21002_ADDR, 0x13, 0x0E)  # CTRL_REG1: Active mode, 100 Hz output rate

def read_gyroscope():
    """ Read 6 bytes of gyroscope data from FXAS21002 """
    gyro_data = bus.read_i2c_block_data(FXAS21002_ADDR, 0x01, 6)

    # Convert raw data to signed 16-bit values
    x = (gyro_data[0] << 8 | gyro_data[1])
    y = (gyro_data[2] << 8 | gyro_data[3])
    z = (gyro_data[4] << 8 | gyro_data[5])

    # Convert to degrees per second (assuming ±250 dps range, 32768 counts per full scale)
    x_dps = x * (250.0 / 32768.0)
    y_dps = y * (250.0 / 32768.0)
    z_dps = z * (250.0 / 32768.0)

    return x_dps, y_dps, z_dps

if __name__ == "__main__":
    init_fxos8700()
    init_fxas21002()

    while True:
        accel = read_acceleration()
        gyro = read_gyroscope()

        print(f"Accel: X={accel[0]:.2f}g, Y={accel[1]:.2f}g, Z={accel[2]:.2f}g")
        print(f"Gyro:  X={gyro[0]:.2f}dps, Y={gyro[1]:.2f}dps, Z={gyro[2]:.2f}dps")
        print("-" * 40)

        time.sleep(0.5)
