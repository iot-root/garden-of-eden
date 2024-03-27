import argparse
from gpiozero import PWMLED
from gpiozero.pins.pigpio import PiGPIOFactory
import pigpio
import time
# from time import sleep

class Light:
    def __init__(self, pin=18, frequency=8000):
        # pigpiod is running on port 8888
        # self.factory = PiGPIOFactory(host='pigpiod', port=8888)  # Specify the address and port
        self.factory = PiGPIOFactory()
        self.pin = pin
        self.led = PWMLED(self.pin, pin_factory=self.factory)
        self.pi = pigpio.pi()
        self.set_frequency(frequency)

    def on(self):
        if self.led.value > 0:
            print("Light already on, skipping")
            return

        print(f"Turning light on")
        self.led.value = 1

    def off(self):
        print(f"Turning light off")
        self.led.value = 0
    
    def set_brightness(self, brightness_percentage):
        """
        Wrapper function around set_duty_cycle. Provides more intuitive function name.

        Args:
        - brightness_percentage (int): A value between 0 (off) and 100 (max brightness).
        """
        self.set_duty_cycle(brightness_percentage)

    def get_brightness(self):
        """
        Wrapper function around get_duty_cycle. Provides more intuitive function name.

        Returns:
        - float: The current duty cycle percentage.
        """
        return self.get_duty_cycle()

    def set_frequency(self, frequency):
        print(f"Setting light frequency to {frequency}")
        self.pi.set_PWM_frequency(self.pin, frequency)
    
    def set_duty_cycle(self, duty_cycle_percentage):
        """
        Set the duty cycle percentage, i.e. bightness level.

        Args:
        - duty_cycle_percentage (int): A value between 0 (off) and 100 (full brightness).
        """
        if 0 <= duty_cycle_percentage <= 100:
            # gpiozero's PWMLED uses a 0-1 scale for duty cycle
            duty = duty_cycle_percentage / 100.0
            print(f"Setting light duty_cycle to {duty_cycle_percentage}%")
            self.led.value = duty
        else:
            raise ValueError("Speed must be between 0 and 100")
        
    def get_duty_cycle(self):
        """
        Get the current duty cycle percentage.

        Returns:
        - float: The current duty cycle percentage.
        """
        duty_cycle = self.led.value * 100
        print(f"Light duty_cycle is {duty_cycle}%")
        return duty_cycle

    def close(self):
        self.led.close()
        self.pi.stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control an IoT light.')
    parser.add_argument('--on', action='store_true', help='Turn the light on.')
    parser.add_argument('--off', action='store_true', help='Turn the light off.')
    parser.add_argument('--brightness', type=int, default=None,
                        help='Set the brightness level (0-100).')

    args = parser.parse_args()

    light = Light(18)  # Default frequency of 8kHz

    if args.on:
        light.on()
        if args.brightness is not None:
            light.set_brightness(args.brightness)
    elif args.off:
        light.off()
    elif args.brightness is not None:
        light.on()
        light.set_brightness(args.brightness)
    else:
        print("No action specified. Use --on, --off, or --brightness.")
