"""
This module provides functionality to read temperature values from the AM2320 sensor 
using the adafruit_ahtx0 library. The CachedSensor class caches the readings for a 
specified duration to prevent redundant reads.
"""

import time
import board
import adafruit_ahtx0
import logging


class CachedSensor:
    """
    Base class for sensors, introducing a caching mechanism for sensor readings.
    """
    
    def __init__(self, sensor, cache_duration=2):
        """
        Initialize the CachedSensor.

        :param sensor: Sensor object for reading values.
        :param cache_duration: Duration (in seconds) to cache the sensor reading. Default is 2 seconds.
        """
        self._sensor = sensor
        self._cache_duration = cache_duration
        self._last_read_time = 0
        self._cached_value = None

    def _read(self):
        """
        Abstract method to fetch the sensor reading. 
        This should be implemented by the subclasses.
        """
        raise NotImplementedError

    def get_value(self):
        """
        Get the sensor reading. If the cached value is older than the specified cache duration, 
        fetch a new reading.

        :return: Cached sensor reading (float).
        """
        current_time = time.time()
        if current_time - self._last_read_time > self._cache_duration or self._cached_value is None:
            self._cached_value = self._read()
            self._last_read_time = current_time
        return self._cached_value

class TemperatureSensor(CachedSensor):
    """
    Sensor class specific to reading temperature values.
    """
    
    def _read(self):
        """
        Fetch the temperature reading from the sensor.

        :return: Temperature value (float).
        """
        return self._sensor.temperature

temperature_sensor = None 

try:
    i2c = board.I2C()
    base_sensor = adafruit_ahtx0.AHTx0(i2c, address=0x38)
    temperature_sensor = TemperatureSensor(base_sensor)
except:
    logging.info("Failed to initiate temperature sensor")

if __name__ == "__main__":
    """
    If the module is executed as a standalone script, it will return the temperature in a telegraf friendly format. 
    """
    try:
        temperature = temperature_sensor.get_value()
        logging.info(f"temperature, value={temperature:.2f}")
    except Exception as e:
        logging.info(f"Error: {e}")
    except KeyboardInterrupt:
        logging.info("Script interrupted.")
