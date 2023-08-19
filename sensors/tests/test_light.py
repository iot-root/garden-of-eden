import unittest
from unittest.mock import patch, Mock
from light import Light

class TestLight(unittest.TestCase):

    @patch('light.PWMLED')
    @patch('light.PiGPIOFactory')
    @patch('light.pigpio.pi')
    def setUp(self, MockPi, MockFactory, MockLED):
        self.mock_led = MockLED.return_value
        self.mock_pi = MockPi.return_value
        self.light = Light(18)

    def test_on(self):
        self.light.on()
        self.assertEqual(self.mock_led.value, 1)

    def test_off(self):
        self.light.off()
        self.assertEqual(self.mock_led.value, 0)

    def test_adjust_valid(self):
        valid_brightness = 0.7
        self.light.adjust(valid_brightness)
        self.assertEqual(self.mock_led.value, valid_brightness)

    def test_adjust_invalid(self):
        with self.assertRaises(ValueError):
            self.light.adjust(1.5)

    def test_set_frequency(self):
        freq = 10000  # 10kHz
        self.light.set_frequency(freq)
        self.mock_pi.set_PWM_frequency.assert_called_with(18, freq)

    def test_close(self):
        self.light.close()
        self.mock_led.close.assert_called_once()
        self.mock_pi.stop.assert_called_once()

if __name__ == '__main__':
    unittest.main()
