import unittest

from app.lib.water import gallons_remaining, is_water_low


class WaterLowTestCase(unittest.TestCase):
    def test_low_when_distance_exceeds_threshold(self):
        # 15cm gap to the surface, alert above 11cm -> low.
        self.assertTrue(is_water_low(15.0, 11.0))

    def test_not_low_when_distance_within_threshold(self):
        self.assertFalse(is_water_low(8.0, 11.0))

    def test_equal_is_not_low(self):
        self.assertFalse(is_water_low(11.0, 11.0))

    def test_disabled_threshold_never_low(self):
        self.assertFalse(is_water_low(99.0, 0))
        self.assertFalse(is_water_low(99.0, None))

    def test_failed_reading_not_low(self):
        self.assertFalse(is_water_low(None, 11.0))


class GallonsRemainingTestCase(unittest.TestCase):
    def test_linear_map(self):
        # full=5cm -> capacity, empty=20cm -> 0, midpoint -> half.
        self.assertEqual(gallons_remaining(5, 5, 20, 5), 5.0)
        self.assertEqual(gallons_remaining(20, 5, 20, 5), 0.0)
        self.assertEqual(gallons_remaining(12.5, 5, 20, 5), 2.5)

    def test_clamps_out_of_range(self):
        self.assertEqual(gallons_remaining(2, 5, 20, 5), 5.0)  # over-full
        self.assertEqual(gallons_remaining(99, 5, 20, 5), 0.0)  # past empty

    def test_guards(self):
        self.assertIsNone(gallons_remaining(None, 5, 20, 5))  # bad reading
        self.assertIsNone(gallons_remaining(10, 5, 20, 0))  # no capacity
        self.assertIsNone(gallons_remaining(10, 20, 20, 5))  # zero span


if __name__ == "__main__":
    unittest.main()
