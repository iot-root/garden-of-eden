"""
This module provides functionality to read temperature values from the AM2320 sensor 
using the adafruit_ahtx0 library.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import config  

class TemperatureSensor:
    """
    Sensor class specific to reading temperature values.
    """
    def __init__(self, sensor):
        self._sensor = sensor

    def read(self):
        """
        Fetch the temperature reading from the sensor.

        :return: Temperature value (float).
        """
        return self._sensor.temperature

temperature_sensor = None 

def get_temperature_sensor():
    global temperature_sensor
    if temperature_sensor is not None:
        return temperature_sensor
    try:
        import board
        import adafruit_ahtx0
        import adafruit_am2320

        i2c = board.I2C()
        if config.SENSOR_TYPE == 'AM2320':
            base_sensor = adafruit_am2320.AM2320(i2c)
        elif config.SENSOR_TYPE == 'DHT20':
            base_sensor = adafruit_ahtx0.AHTx0(i2c, address=0x38)
        else:
            raise ValueError("Unsupported sensor type")
        temperature_sensor = TemperatureSensor(base_sensor)
    except Exception:
        print("Failed to initiate temperature sensor")
    return temperature_sensor

if __name__ == "__main__":
    """
    If the module is executed as a standalone script, it will return the temperature in a telegraf friendly format. 
    """
    try:
        temperature = get_temperature_sensor().read()
        print(f"temperature, value={temperature:.2f}")
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Script interrupted.")
