# coding=utf-8
import time
import RPi.GPIO as GPIO
from .config import (
    CHANNEL_WATER_LVL_IN,
    CHANNEL_WATER_LVL_OUT,
    TIMEOUT_WATER_LVL,
)

class WaterLevelMeasurementTimeout(Exception):
    """
    Raised when the water level measurement exceeds the allowed timeout.
    """
    def __init__(self, timeout, channel_in, channel_out):
        self.timeout = timeout
        self.channel_in = channel_in
        self.channel_out = channel_out
        super().__init__(self._generate_message())

    def _generate_message(self):
        return (
            f"Water level measurement timeout after {self.timeout} seconds. "
            f"Using input channel {self.channel_in} and output channel {self.channel_out}."
        )

class WaterLevel:
    """
    Class to handle water level measurements using the Raspberry Pi GPIO.

    Attributes:
        None

    Methods:
        __init__(): Initializes the GPIO settings and waits for the sensor to settle.
        measure_once(): Measures the water level once and returns the distance in cm.
        measure(): Measures the water level multiple times and returns the average of the median values.
        median(data): Returns the median value from a list of numbers.
    """

    def __init__(self):
        """
        Initializes the GPIO settings and waits for the sensor to settle.
        """
        if not GPIO.getmode():
            GPIO.setmode(GPIO.BCM)  # Numbers GPIOs by GPIO pin, not physical location
        GPIO.setup(CHANNEL_WATER_LVL_OUT, GPIO.OUT)
        GPIO.setup(CHANNEL_WATER_LVL_IN, GPIO.IN)
        GPIO.output(CHANNEL_WATER_LVL_OUT, GPIO.LOW)
        print("Waiting 5s For Sensor To Settle")
        time.sleep(5)

    def measure_once(self):
        """
        Measures the water level once using the GPIO pins.
        
        Returns:
            float: The measured distance in cm.
        """
        GPIO.output(CHANNEL_WATER_LVL_OUT, GPIO.HIGH)
        time.sleep(0.00003)
        GPIO.output(CHANNEL_WATER_LVL_OUT, GPIO.LOW)
        timeout = time.time() + TIMEOUT_WATER_LVL

        while (
            GPIO.input(CHANNEL_WATER_LVL_IN) == GPIO.LOW
            and timeout > time.time()
        ):
            pulse_start = time.time()

        while (
            GPIO.input(CHANNEL_WATER_LVL_IN) == GPIO.HIGH
            and timeout > time.time()
        ):
            pulse_end = time.time()

        if timeout < time.time():
            raise WaterLevelMeasurementTimeout(TIMEOUT_WATER_LVL, CHANNEL_WATER_LVL_IN, CHANNEL_WATER_LVL_OUT)
        
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        print(
            "[{}] - Water Level Distance: {} cm".format(
                time.ctime(time.time()), distance
            )
        )
        return distance

    def measure(self):
        """
        Measures the water level multiple times and returns the average of the median values.
        
        Returns:
            float: The average of the median water level measurements in cm.
        """
        measurements = []
        for _ in range(10):
            try:
                measurement = self.measure_once()
                measurements.append(measurement)
            except Exception:
                pass
        median_list = self.median(measurements)
        return round(sum(median_list) / len(median_list), 2)

    def median(self, data):
        """
        Returns the median value from a list of numbers.
        
        Args:
            data (list): A list of water distance measurements.
        
        Returns:
            float: The median value.
        """
        if not isinstance(data, list):
            return ""
        sorted_data = sorted(data)
        data_length = len(data)
        if data_length % 2 > 0:
            return sorted_data[data_length // 2 : data_length // 2 + 1]
        else:
            mid = data_length // 2
            return (sorted_data[mid - 1] + sorted_data[mid]) / 2

if __name__ == "__main__":
    water_level_instance = water_level()

    try:
        print("Measuring water level:")
        water_level_value = water_level_instance.measure()
        print("Level is:")
        print(water_level_value)

    except KeyboardInterrupt:
        print("Script interrupted.")
