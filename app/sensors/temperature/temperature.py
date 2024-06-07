"""
This module provides functionality to read humidity and temperature values from the AM2320 or DHT20 sensors using the Adafruit libraries.
The CachedSensor class caches the readings for 2 seconds to avoid redundant reads.
"""

import time
import board
import adafruit_ahtx0
import adafruit_am2320
import os

class CachedSensor:
    """
    Base class for sensors that caches the readings for a specified duration.
    """
    def __init__(self, sensor, cache_duration=2):
        """
        Initialize the CachedSensor object.

        :param sensor: Sensor object
        :param cache_duration: Duration to cache the sensor reading, default is 2 seconds
        """
        self._sensor = sensor
        self._cache_duration = cache_duration
        self._last_read_time = 0
        self._cached_temperature = None

    def _read_temperature(self):
        """
        Fetch the temperature reading. Needs to be implemented by subclasses.
        """
        raise NotImplementedError

    def get_temperature(self):
        """
        Get the cached temperature reading. If the cached value is older than the cache duration,
        fetch a new reading.

        :return: Temperature reading (float)
        """
        current_time = time.time()
        if current_time - self._last_read_time > self._cache_duration or self._cached_temperature is None:
            self._cached_temperature = self._read_temperature()
            self._last_read_time = current_time
        return self._cached_temperature

class TemperatureSensor(CachedSensor):
    """
    Sensor class for reading temperature values.
    """

    def _read_temperature(self):
        """
        Fetch the temperature reading from the sensor.

        :return: Temperature value (float)
        """
        return self._sensor.temperature


temperature_sensor = None
def main(sensor_type):
    try:
        i2c = board.I2C()

        # Initialize the sensor based on sensor_type
        if sensor_type == "DHT20":
            try:
                base_sensor = adafruit_ahtx0.AHTx0(i2c, address=0x38)
                temperature_sensor = TemperatureSensor(base_sensor)
                print("DHT20 sensor initialized.")
            except Exception as e:
                print(f"Failed to initiate DHT20 sensor: {e}")
                raise e

        elif sensor_type == "AM2320":
            try:
                base_sensor = adafruit_am2320.AM2320(i2c)
                temperature_sensor = TemperatureSensor(base_sensor)
                print("AM2320 sensor initialized.")
            except Exception as e:
                print(f"Failed to initiate AM2320 sensor: {e}")
                raise e

        else:
            print(f"Unknown sensor type specified: {sensor_type}")
            raise ValueError(f"Unsupported sensor type: {sensor_type}")

    except Exception as e:
        print(f"Error initializing sensors: {e}")

    if temperature_sensor:
        try:
            temperature = temperature_sensor.get_temperature()
            print(f"temperature, value={temperature:.2f}")
        except Exception as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("Script interrupted.")
    else:
        print("No temperature sensor available.")

if __name__ == "__main__":
    sensor_type = "AM2320"
    main(sensor_type)