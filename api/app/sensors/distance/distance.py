# coding=utf-8
from gpiozero import DistanceSensor
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import argparse
import logging
import json
from datetime import datetime

class MeasurementError(Exception):
    """
    Raised when there's an error in distance measurement.
    """
    def __init__(self, message):
        super().__init__(message)

class Distance:
    """
    Class to handle distance measurements using the Raspberry Pi GPIO with gpiozero.
    Attributes:
        sensor: DistanceSensor object from gpiozero.
    """
    def __init__(self, pin_factory=None):
        """
        Initializes the DistanceSensor object.
        """

        # Ensure the pin factory is either provided or defaults to PiGPIOFactory
        self.pin_factory = pin_factory if pin_factory else PiGPIOFactory()

        # Initialize the DistanceSensor with the specified or default pin factory
        self.sensor = DistanceSensor(echo=19, trigger=26, pin_factory=self.pin_factory)

    def measure_once(self):
        """
        Measures the distance once.
        Returns:
            float: The measured distance in centimeters.
        """
        distance = self.sensor.distance * 100  # Convert to cm
        # log(f"Measured Distance: {distance:.2f} cm")
        return round(distance, 2)

    def measure(self):
        """
        Measures the distance multiple times and returns the average of the median values.
        Returns:
            float: The average of the median distance measurements in cm.
        """
        measurements = []
        for _ in range(10):
            try:
                measurement = self.measure_once()
                measurements.append(measurement)
            except Exception:
                pass
        median_value = self.median(measurements)
        return round(sum(median_value) / len(median_value), 2)

    def median(self, data):
        """
        Returns the median value from a list of numbers.
        Args:
            data (list): A list of distance measurements.
        Returns:
            list[float]: A list containing the median value.
        """
        if not isinstance(data, list) or not data:
            raise MeasurementError("Invalid data for median calculation")
        sorted_data = sorted(data)
        data_length = len(data)
        if data_length % 2 > 0:
            return [sorted_data[data_length // 2]]
        else:
            # If two medians, use an average of both
            mid = data_length // 2
            return [(sorted_data[mid - 1] + sorted_data[mid]) / 2]

if __name__ == "__main__":
    """
    If the module is executed as a standalone script, it will return the distance in json.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(description='Control a distance sensor.')
    parser.add_argument('--log', action='store_true')
    args = parser.parse_args()

    sensor = None
    try:
        sensor = Distance()
    except:
        logging.info(f"Failed to initialize distance sensor")
        exit(1)

    if args.log:
        try:
            distance = sensor.measure()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = {
                "timestamp": timestamp,
                "sensor": "Distance",
                "value": f"{distance:.2f}"
            }
            logging.info(json.dumps(log_entry))
            print(json.dumps(log_entry))
        except Exception as e:
            logging.info(f"Error: {e}")
        except KeyboardInterrupt:
            logging.info("Script interrupted.")
    else:
        logging.info("No action specified. Use --log.")
