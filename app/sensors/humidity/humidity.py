"""
This module provides functionality to read humidity values from the AM2320 sensor 
using the adafruit_ahtx0 library.
"""

import time
import board
import adafruit_ahtx0
import adafruit_am2320

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import config  

class HumiditySensor:
    """
    Sensor class specific to reading humidity values.
    """
    def __init__(self, sensor):
        self._sensor = sensor

    def read(self):
        """
        Fetch the humidity reading from the sensor.

        :return: Humidity value (float).
        """
        return self._sensor.relative_humidity

humidity_sensor = None 

try:
    i2c = board.I2C()
    if config.SENSOR_TYPE == 'AM2320':
        base_sensor = adafruit_am2320.AM2320(i2c, address=0x5C)
    elif config.SENSOR_TYPE == 'DHT20':
        base_sensor = adafruit_ahtx0.AHTx0(i2c, address=0x38)
    else:
        raise ValueError("Unsupported sensor type")
    humidity_sensor = HumiditySensor(base_sensor)
except:
    print("Failed to initiate humidity sensor")

if __name__ == "__main__":
    """
    If the module is executed as a standalone script, it will return the humidity in a telegraf friendly format. 
    """
    try:
        humidity = humidity_sensor.read()
        print(f"humidity, value={humidity:.2f}")
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Script interrupted.")