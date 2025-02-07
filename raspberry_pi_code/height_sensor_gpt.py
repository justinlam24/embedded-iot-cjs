import time
from smbus2 import SMBus

def read_distance(adc_address=0x48, bus_num=1):
    """
    Reads the distance from the LV-MaxSonar-E2 sensor via an ADS1115 ADC.
    
    The sensor's analog output is scaled via a resistor divider (R1=10kΩ, R2=20kΩ)
    so that a 5V output is reduced to ~3.33V, safe for the ADS1115 (which is powered at 3.3V).
    
    The ADS1115 is configured for:
      - Single-ended input on channel 0
      - Gain = 1 (±4.096V full-scale)
      - Single-shot mode, 128 samples per second
      - Comparator disabled
      
    The sensor outputs approximately 9.8 mV per inch. The function converts the measured voltage 
    back to the original sensor voltage and then calculates the distance in centimeters.
    
    Parameters:
      adc_address: I2C address of the ADS1115 (default 0x48)
      bus_num:     I2C bus number (default 1, as on most Raspberry Pis)
      
    Returns:
      distance_cm: Calculated distance in centimeters.
    """
    # ADS1115 configuration for channel 0, gain=1, single-shot mode, 128 SPS.
    # See explanation above for how 0xC383 is obtained.
    config = 0xC383  
    # Prepare the 2 bytes to send (big-endian format)
    config_bytes = [(config >> 8) & 0xFF, config & 0xFF]
    
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

# Example usage:
if __name__ == '__main__':
    distance = read_distance()
    print("Distance: {:.2f} cm".format(distance))

