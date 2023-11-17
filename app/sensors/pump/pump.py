import argparse
from gpiozero import PWMLED
from gpiozero.pins.pigpio import PiGPIOFactory
import pigpio
from time import sleep

class Pump:
    def __init__(self, pin=24, frequency=50):
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
        Turn pump on. Default to 30 percent duty.
        """
        print(f"Turning pump on")
        self.pump.value = 1

    def off(self):
        """
        Turn pump off.
        """
        print(f"Turning pump off")
        self.pump.value = 0

    def set_speed(self, speed_percentage):
        """
        Wrapper function around set_duty_cycle. Provides more intuitive function name.

        Args:
        - speed_percentage (int): A value between 0 (stopped) and 100 (max speed).
        """
        self.set_duty_cycle(speed_percentage)

    def get_speed(self):
        """
        Wrapper function around get_duty_cycle. Provides more intuitive function name.

        Returns:
        - float: The current duty cycle percentage.
        """
        return self.get_duty_cycle()

    def set_frequency(self, frequency):
        """
        Change driving frequency.
        """
        print(f"Setting pump frequency to {frequency}")
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
            print(f"Setting pump duty_cycle to {duty_cycle_percentage}%")
            self.pump.value = duty
        else:
            raise ValueError("Speed must be between 0 and 1")
    
    def get_duty_cycle(self):
        """
        Get the current duty cycle percentage.

        Returns:
        - float: The current duty cycle percentage.
        """
        duty_cycle_percentage = self.pump.value * 100
        print(f"Pump duty_cycle is {duty_cycle_percentage}%")
        return duty_cycle_percentage

    def close(self):
        self.pump.close()
        self.pi.stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control a pump.')
    parser.add_argument('--on', action='store_true', help='Turn the pump on.')
    parser.add_argument('--off', action='store_true', help='Turn the pump off.')
    parser.add_argument('--speed', type=int, default=None, help='Set the pump speed (0-100).')

    args = parser.parse_args()

    pump = Pump(24)  # Default frequency of 50Hz

    if args.on:
        pump.on()
        if args.speed is not None:
            pump.set_speed(args.speed)
    elif args.off:
        pump.off()
    elif args.speed is not None:
        pump.on()
        pump.set_speed(args.speed)
    else:
        print("No action specified. Use --on, --off, or --speed.")