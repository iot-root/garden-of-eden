from gpiozero import PWMLED
from gpiozero.pins.pigpio import PiGPIOFactory
import pigpio
from time import sleep

class Pump:
    def __init__(self, pin, frequency=50):
        # Specify the pigpiod address and port
        self.factory = PiGPIOFactory()
        # For Docker will will do...
        # self.factory = PiGPIOFactory(host='pigpiod', port=8888)
        self.pin = pin
        self.pump = PWMLED(self.pin, pin_factory=self.factory)
        self.pi = pigpio.pi()
        self.set_frequency(frequency)

    def on(self):
        """
        Turn pump on
        """
        self.pump.value = 1

    def off(self):
        """
        Turn pump off.
        """
        self.pump.value = 0

    def set_speed(self, speed_percentage):
        """
        Wrapper function around set_duty_cycle. Provides more intuitive function name.

        Args:
        - speed_percentage (int): A value between 0 (stopped) and 100 (max speed).
        """
        self.set_duty_cycle(speed_percentage)

    def get_speed(self, speed_percentage):
        """
        Wrapper function around get_duty_cycle. Provides more intuitive function name.

        Returns:
        - float: The current duty cycle percentage.
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
            self.pump.value = duty
        else:
            raise ValueError("Speed must be between 0 and 1")
    
    def get_duty_cycle(self):
        """
        Get the current duty cycle percentage.

        Returns:
        - float: The current duty cycle percentage.
        """
        return self.pump.value * 100

    def close(self):
        self.pump.close()
        self.pi.stop()

if __name__ == '__main__':
    # Usage example:
    pump = Pump(24)  # Default frequency of 8kHz
    pump.on()
    pump.set_speed(30)  # Adjust to 30% brightness
    sleep(4)
    pump.off()
    pump.close()
