import unittest
from unittest.mock import patch
import sys
import os
# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.sensors.light.light import Light

class TestLight(unittest.TestCase):
    @patch('app.sensors.light.light.PWMLED')
    @patch('app.sensors.light.light.PiGPIOFactory')
    @patch('app.sensors.light.light.pigpio.pi')
    def setUp(self, MockPi, MockFactory, MockPWMLED):
        self.mock_led = MockPWMLED.return_value
        self.mock_led.value = 0
        self.mock_pi = MockPi.return_value
        self.light = Light(18)

    def test_turn_on_from_0(self):
        self.mock_led.value = 0
        self.light.on()
        self.assertEqual(self.mock_led.value, 1)
        self.assertLogs('Turning light on')

    def test_turn_on_from_nonzero(self):
        self.mock_led.value = 0.5
        self.light.on()
        self.assertEqual(self.mock_led.value, 0.5)
        self.assertLogs('Light already on, skipping')

    def test_off(self):
        self.mock_led.value = 1
        self.light.off()
        self.assertEqual(self.mock_led.value, 0)
        self.assertLogs('Turning light off')

    def test_set_brightness_valid(self):
        valid_brightness = 70
        self.light.set_brightness(valid_brightness)
        self.assertEqual(self.mock_led.value * 100, valid_brightness)

    def test_set_brightness_invalid(self):
        with self.assertRaises(ValueError):
            self.light.set_brightness(110)

    def test_set_frequency(self):
        freq = 10000  # 10kHz
        self.light.set_frequency(freq)
        self.mock_pi.set_PWM_frequency.assert_called_with(18, freq)

    def test_close(self):
        self.light.close()
        self.mock_led.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
