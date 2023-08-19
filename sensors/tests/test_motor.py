import unittest
from unittest.mock import patch, Mock
from motor import Motor  # Assuming the above code is saved in a file named 'motor.py'

class TestMotor(unittest.TestCase):

    @patch('motor.PWMLED')
    @patch('motor.PiGPIOFactory')
    @patch('motor.pigpio.pi')
    def setUp(self, MockPi, MockFactory, MockPWMLED):
        self.mock_pwm_motor = MockPWMLED()
        self.mock_pwm_motor.value = Mock()  # Set an initial value as a new Mock
        self.mock_pi = MockPi()
        self.motor = Motor(24)

    def test_on(self):
        self.motor.on()
        self.assertEqual(self.mock_pwm_motor.value, 1)

    def test_off(self):
        self.motor.off()
        self.assertEqual(self.mock_pwm_motor.value, 0)

    def test_set_speed(self):
        self.motor.set_speed(50)
        self.assertEqual(self.mock_pwm_motor.value, 0.5)

    def test_set_frequency(self):
        freq = 1000
        self.motor.set_frequency(freq)
        self.mock_pi.set_PWM_frequency.assert_called_with(24, freq)

    def test_set_duty_cycle_valid(self):
        self.motor.set_duty_cycle(30)
        self.assertEqual(self.mock_pwm_motor.value, 0.3)

    def test_set_duty_cycle_invalid_low(self):
        with self.assertRaises(ValueError):
            self.motor.set_duty_cycle(-1)

    def test_set_duty_cycle_invalid_high(self):
        with self.assertRaises(ValueError):
            self.motor.set_duty_cycle(101)

    def test_close(self):
        self.motor.close()
        self.mock_pwm_motor.close.assert_called_once()
        self.mock_pi.stop.assert_called_once()

if __name__ == '__main__':
    unittest.main()
