from gpiozero import PWMLED
from gpiozero.pins.pigpio import PiGPIOFactory
import pigpio
from time import sleep

class Motor:
    def __init__(self, pin, frequency=50):
        # Specify the pigpiod address and port
        self.factory = PiGPIOFactory()
        # For Docker will will do...
        # self.factory = PiGPIOFactory(host='pigpiod', port=8888)
        self.pin = pin
        self.motor = PWMLED(self.pin, pin_factory=self.factory)
        self.pi = pigpio.pi()
        self.set_frequency(frequency)

    def on(self):
        """
        Turn pump on
        """
        self.motor.value = 1

    def off(self):
        """
        Turn pump off.
        """
        self.motor.value = 0

    def set_speed(self, speed_percentage):
        """
        Wrapper function around set_duty_cycle. Provides more intuitive function name.

        Args:
        - speed_percentage (int): A value between 0 (stopped) and 100 (max speed).
        """
        self.set_duty_cycle(speed_percentage)

    def set_frequency(self, frequency):
        """
        Change driving frequency.
        """
        self.pi.set_PWM_frequency(self.pin, frequency)

    def set_duty_cycle(self, duty_cycle_percentage):
        """
        Adjust the speed of the pump.

        Args:
        - duty_cycle_percentage (int): A value between 0 (off) and 100 (full brightness).
        """
        if 0 <= duty_cycle_percentage <= 100:
            # gpiozero's PWMLED uses a 0-1 scale for duty cycle
            duty = duty_cycle_percentage / 100.0
            self.motor.value = duty
        else:
            raise ValueError("Speed must be between 0 and 1")

    def close(self):
        self.motor.close()
        self.pi.stop()

if __name__ == '__main__':
    # Usage example:
    motor = Motor(24)  # Default frequency of 8kHz
    motor.on()
    motor.set_speed(30)  # Adjust to 30% brightness
    sleep(4)
    motor.off()
    motor.close()
