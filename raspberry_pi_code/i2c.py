import time
import smbus2

class Sensor:
    # I2C Addresses
    FXOS8700_ADDR = 0x1F  # Accelerometer + Magnetometer
    FXAS21002_ADDR = 0x21  # Gyroscope
    config = 0xC383
    config_bytes = [(config >> 8) & 0xff, config & 0xFF]
    # I2C Bus
    adc_address = 0x48
    bus_num = 1
    def __init__(self):

        self.bus = smbus2.SMBus(1)
        self.init_fxos8700()
        self.init_fxas21002()

    def init_fxos8700(self):
        """ Initialize the FXOS8700 accelerometer """
        # Set device to active mode
        try:
            self.bus.write_byte_data(self.FXOS8700_ADDR, 0x2A, 0x01)
            print("I2C write successful!")
        except OSError as e:
            print(f"I2C write failed: {e}")

    def accelerometer(self):
        """ Read 6 bytes of acceleration data from FXOS8700 """
        accel_data = self.bus.read_i2c_block_data(FXOS8700_ADDR, 0x01, 6)

        # Convert raw data to signed 14-bit values, since I2C transfers data in 8-bit bytes
        x = (accel_data[0] << 8 | accel_data[1]) >> 2
        y = (accel_data[2] << 8 | accel_data[3]) >> 2
        z = (accel_data[4] << 8 | accel_data[5]) >> 2

        # Convert to G-force (assuming ±2g range, 8192 counts per g)
        g = 9.80665
        x_g = x * g / 4096.0
        y_g = y * g / 4096.0
        z_g = z * g / 4096.0

        return x_g, y_g, z_g

    def init_fxas21002(self):
        """ Initialize the FXAS21002 gyroscope """
        self.bus.write_byte_data(self.FXAS21002_ADDR, 0x13, 0x00)  # CTRL_REG1: Standby mode
        self.bus.write_byte_data(self.FXAS21002_ADDR, 0x13, 0x0E)  # CTRL_REG1: Active mode, 100 Hz output rate

    def gyroscope(self):
        """ Read 6 bytes of gyroscope data from FXAS21002 """
        gyro_data = self.bus.read_i2c_block_data(self.FXAS21002_ADDR, 0x01, 6)

        # Convert raw data to signed 16-bit values
        x = (gyro_data[0] << 8 | gyro_data[1])
        y = (gyro_data[2] << 8 | gyro_data[3])
        z = (gyro_data[4] << 8 | gyro_data[5])

        # Convert to degrees per second (assuming ±250 dps range, 32768 counts per full scale)
        x_dps = x * (250.0 / 32768.0)
        y_dps = y * (250.0 / 32768.0)
        z_dps = z * (250.0 / 32768.0)

        return x_dps, y_dps, z_dps

    def ultrasonic(self):
        with SMBus(bus_num) as bus:

            # Write the config bytes to register 0x01 (config register)
            bus.write_i2c_block_data(adc_address, 0x01, config_bytes)
            
            # Wait for the conversion to complete.
            # With 128 SPS, conversion time is about 7.8 ms; waiting 10 ms is safe.
            time.sleep(0.01)
            
            # Read the conversion register (0x00). The ADS1115 returns a 16-bit value.
            result = bus.read_word_data(adc_address, 0x00)
            
            # The ADS1115 outputs data in big-endian order but read_word_data may give little-endian.
            # Swap the bytes.
            result = ((result & 0xFF) << 8) | (result >> 8)
            
            # For single-ended measurements, the result should be positive.
            # (If you wish to handle negative values, you can convert from two's complement.)
            if result > 0x7FFF:
                result -= 0x10000
            
            # Convert the ADC reading to the voltage at the ADS1115 input.
            # For gain=1, the ADS1115 full-scale is ±4.096 V.
            # The ADS1115 is 16-bit so 32768 steps (using 32768 because the range is -32768 to +32767).
            voltage_adc = result * (4.096 / 32768.0)
            
            # Undo the resistor divider.
            # With R1 = 10kΩ and R2 = 20kΩ, the divider factor is (R1+R2)/R2 = 1.5.
            sensor_voltage = voltage_adc * 1.5
            
            # Convert the sensor voltage to a distance.
            # The sensor outputs about 9.8 mV per inch.
            # (Note: 0.0098 V per inch.)
            distance_inches = sensor_voltage / 0.0098
            
            # Convert inches to centimeters (1 inch = 2.54 cm)
            distance_cm = distance_inches * 2.54
            
            return distance_cm        

if __name__ == "__main__":
    init_fxos8700()
    init_fxas21002()
    configure_adc()
    voltage = read_adc()

    while True:
        accel = read_acceleration()
        gyro = read_gyroscope()

        print(f"Accel: X={accel[0]:.2f}g, Y={accel[1]:.2f}g, Z={accel[2]:.2f}g")
        print(f"Gyro:  X={gyro[0]:.2f}dps, Y={gyro[1]:.2f}dps, Z={gyro[2]:.2f}dps")
        print("-" * 40)
        print(f"ADC Voltage: {voltage:.3f} V")
        
        time.sleep(0.5)
