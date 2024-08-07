# distance.py

from gpiozero import DistanceSensor
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

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
        sensor (DistanceSensor): The DistanceSensor object for distance measurements.
        pin_factory (PiGPIOFactory): The factory for GPIO pin configuration.
    """

    def __init__(self, pin_factory=None):
        """
        Initializes the DistanceSensor object with the specified or default pin factory.

        Args:
            pin_factory (PiGPIOFactory, optional): A custom pin factory for GPIO configuration. Defaults to PiGPIOFactory.

        Raises:
            MeasurementError: If the DistanceSensor fails to initialize.
        """
        self.pin_factory = pin_factory if pin_factory else PiGPIOFactory()
        try:
            self.sensor = DistanceSensor(echo=19, trigger=26, pin_factory=self.pin_factory)
        except Exception as e:
            raise MeasurementError(f"Failed to initialize DistanceSensor: {e}")

    def measure_once(self):
        """
        Measures the distance once.

        Returns:
            float: The measured distance in centimeters.

        Raises:
            MeasurementError: If the measurement fails.
        """
        try:
            distance = self.sensor.distance * 100  # Convert to cm
            return round(distance, 2)
        except Exception as e:
            raise MeasurementError(f"Measurement failed: {e}")

    def measure(self):
        """
        Measures the distance multiple times and returns the average of the median values.

        Returns:
            float: The average of the median distance measurements in cm.

        Raises:
            MeasurementError: If no successful measurements are obtained.
        """
        measurements = []
        for _ in range(10):
            try:
                measurement = self.measure_once()
                measurements.append(measurement)
            except MeasurementError:
                pass  # Handle individual measurement errors gracefully
        if not measurements:
            raise MeasurementError("No successful measurements")
        median_value = self.median(measurements)
        return round(sum(median_value) / len(median_value), 2)

    def median(self, data):
        """
        Returns the median value from a list of numbers.

        Args:
            data (list): A list of distance measurements.

        Returns:
            list[float]: A list containing the median value.

        Raises:
            MeasurementError: If the data is invalid.
        """
        if not isinstance(data, list) or not data:
            raise MeasurementError("Invalid data for median calculation")
        sorted_data = sorted(data)
        data_length = len(data)
        if data_length % 2 > 0:
            return [sorted_data[data_length // 2]]
        else:
            mid = data_length // 2
            return [(sorted_data[mid - 1] + sorted_data[mid]) / 2]

if __name__ == "__main__":
    """
    If the module is executed as a standalone script, it will return the distance in a telegraf friendly format.
    """
    try:
        distance_instance = Distance()
        distance = distance_instance.measure()
        print(f"distance, value={distance:.2f}")
    except MeasurementError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Script interrupted.")
