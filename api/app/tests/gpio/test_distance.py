import unittest
from unittest.mock import patch, Mock
import sys
import os
# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.sensors.distance.distance import Distance, MeasurementError

class TestDistance(unittest.TestCase):

    @patch('app.sensors.distance.distance.DistanceSensor', autospec=True)
    def setUp(self, MockDistanceSensor):
        # Mock the behavior of the DistanceSensor so it returns some fixed values
        self.mock_sensor = MockDistanceSensor.return_value
        self.mock_sensor.distance = 0.5
        self.distance = Distance()

    def assertAlmostEqual(self, a, b, places=5):
        # An epsilon check for floating-point comparisons
        self.assertTrue(abs(a-b) < 10**(-places))

    def test_measure_once(self):
        measured_distance = self.distance.measure_once()
        self.assertAlmostEqual(measured_distance, 50.00)

    def test_median_odd_length(self):
        data = [1, 2, 3, 4, 5]
        median_value = self.distance.median(data)
        self.assertEqual(median_value, [3])

    def test_median_even_length(self):
        data = [1, 2, 3, 4, 5, 6]
        median_value = self.distance.median(data)
        self.assertEqual(median_value, [3.5])

    def test_median_with_empty_data(self):
        with self.assertRaises(MeasurementError):
            self.distance.median([])

    def test_median_with_non_list(self):
        with self.assertRaises(MeasurementError):
            self.distance.median("string")

    @patch('app.sensors.distance.distance.Distance.measure_once', autospec=True) 
    def test_measure(self, mock_measure_once):
        mock_measure_once.side_effect = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        measured_distance = self.distance.measure()
        self.assertAlmostEqual(measured_distance, 55.00)

if __name__ == "__main__":
    unittest.main()
