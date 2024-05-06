"""
This module provides functionality to read humidity values from the AM2320 sensor using the adafruit_ahtx0 library.
The CachedSensor class caches the readings for 2 seconds to avoid redundant reads.
"""

import time
import board
import adafruit_ahtx0

class CachedSensor:
    """
    Base class for sensors that caches the readings for a specified duration.
    """
    def __init__(self, sensor, cache_duration=200):
        """
        Initialize the CachedSensor object.

        :param sensor: Sensor object
        :param cache_duration: Duration to cache the sensor reading, default is 2 seconds
        """
        self._sensor = sensor
        self._cache_duration = cache_duration
        self._last_read_time = 0
        self._cached_value = None

    def _read(self):
        """
        Fetch the sensor reading. Needs to be implemented by subclasses.
        """
        raise NotImplementedError

    def get_value(self):
        """
        Get the cached sensor reading. If the cached value is older than the cache duration,
        fetch a new reading.

        :return: Sensor reading (float)
        """
        current_time = time.time()
        if current_time - self._last_read_time > self._cache_duration or self._cached_value is None:
            self._cached_value = self._read()
            self._last_read_time = current_time
        return self._cached_value

class HumiditySensor(CachedSensor):
    """
    Sensor class for reading humidity values.
    """
    def _read(self):
        """
        Fetch the humidity reading from the sensor.

        :return: Humidity value (float)
        """
        return self._sensor.relative_humidity

humidity_sensor = None
try:
    i2c = board.I2C()
    base_sensor = adafruit_ahtx0.AHTx0(i2c, address=0x38)
    humidity_sensor = HumiditySensor(base_sensor)
except:
    logging.info("Failed to initiate humidity sensor")

#todo: add support for AM2320...
# i2c = board.I2C()
# base_sensor = adafruit_ahtx0.AHTx0(i2c, address=0x38)
# humidity_sensor = HumiditySensor(base_sensor)

if __name__ == "__main__":
    """
    If the module is executed as a standalone script, it will return the humidity in a telegraf friendly format. 
    """
    try:
        humidity = humidity_sensor.get_value()
        logging.info(f"humidity, value={humidity:.2f}")
    except Exception as e:
        logging.info(f"Error: {e}")
    except KeyboardInterrupt:
        logging.info("Script interrupted.")
