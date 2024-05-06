import unittest
from unittest.mock import patch, Mock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.sensors.pump.pump import Pump

class TestPump(unittest.TestCase):

    @patch('app.sensors.pump.pump.PWMLED')
    @patch('app.sensors.pump.pump.PiGPIOFactory')
    @patch('app.sensors.pump.pump.pigpio.pi')
    def setUp(self, MockPi, MockFactory, MockPWMLED):
        self.mock_pwm_pump = MockPWMLED()
        self.mock_pwm_pump.value = Mock()  # Set an initial value as a new Mock
        self.mock_pi = MockPi()
        self.pump = Pump(24)

    def test_on(self):
        self.pump.on()
        self.assertEqual(self.mock_pwm_pump.value, 1)

    def test_off(self):
        self.pump.off()
        self.assertEqual(self.mock_pwm_pump.value, 0)

    def test_set_speed(self):
        self.pump.set_speed(50)
        self.assertEqual(self.mock_pwm_pump.value, 0.5)

    def test_set_frequency(self):
        freq = 1000
        self.pump.set_frequency(freq)
        self.mock_pi.set_PWM_frequency.assert_called_with(24, freq)

    def test_set_duty_cycle_valid(self):
        self.pump.set_duty_cycle(30)
        self.assertEqual(self.mock_pwm_pump.value, 0.3)

    def test_set_duty_cycle_invalid_low(self):
        with self.assertRaises(ValueError):
            self.pump.set_duty_cycle(-1)

    def test_set_duty_cycle_invalid_high(self):
        with self.assertRaises(ValueError):
            self.pump.set_duty_cycle(101)

    def test_get_duty_cycle(self):
        self.mock_pwm_pump.value = 0.7
        result = self.pump.get_duty_cycle()
        self.assertEqual(result, 70.0)

    def test_close(self):
        self.pump.close()
        self.mock_pwm_pump.close.assert_called_once()
        self.mock_pi.stop.assert_called_once()

if __name__ == '__main__':
    unittest.main()
