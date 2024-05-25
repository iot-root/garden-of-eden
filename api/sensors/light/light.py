import argparse
from gpiozero import PWMLED
from gpiozero.pins.pigpio import PiGPIOFactory
import pigpio
import logging

logging.basicConfig(level=logging.INFO)

class GPIOController:
    def __init__(self, pin, pin_factory=None):
        self.pin = pin
        self.factory = pin_factory
        if pin_factory:
            self.pi = pigpio.pi()
        else:
            self.pi = pigpio.pi()
        
        if not self.pi.connected:
            raise RuntimeError("Failed to connect to pigpiod daemon. Ensure it's running and accessible.")

    def set_frequency(self, frequency):
        if self.pi:
            self.pi.set_PWM_frequency(self.pin, frequency)
        else:
            raise RuntimeError("pigpio.pi client is not initialized.")

class Light:
    def __init__(self, pin=18, frequency=8000, pin_factory=None):
        # pigpiod is running on port 8888
        # Note: for docker: PiGPIOFactory(host='pigpiod', port=8888)
        self.pin = pin
        self.pin_factory = pin_factory if pin_factory else PiGPIOFactory()
        self.led = PWMLED(self.pin, pin_factory=self.pin_factory)
        self.gpio = GPIOController(pin, pin_factory)
        self.set_frequency(frequency)

    def on(self):
        """
        Turn on lights.
        """
        if self.led.value > 0:
            logging.info("Light already on, skipping")
            return

        logging.info("Turning light on")
        self.led.value = 1

    def off(self):
        """
        Turn off lights.
        """
        logging.info("Turning light off")
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
        logging.info(f"Setting light frequency to {frequency}")
        self.gpio.set_frequency(frequency)
    
    def set_duty_cycle(self, duty_cycle_percentage):
        """
        Set the duty cycle percentage, i.e. brightness level.

        Args:
        - duty_cycle_percentage (int): A value between 0 (off) and 100 (full brightness).
        """
        if 0 <= duty_cycle_percentage <= 100:
            # gpiozero's PWMLED uses a 0-1 scale for duty cycle
            duty = duty_cycle_percentage / 100.0
            logging.info(f"Setting light duty_cycle to {duty_cycle_percentage}%")
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
        logging.info(f"Light duty_cycle is {duty_cycle}%")
        return duty_cycle

    def close(self):
        self.led.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control an IoT light.')
    parser.add_argument('--on', action='store_true', help='Turn the light on.')
    parser.add_argument('--off', action='store_true', help='Turn the light off.')
    parser.add_argument('--brightness', type=int, default=None,
                        help='Set the brightness level (0-100).')
    parser.add_argument('--log', action='store_true')

    args = parser.parse_args()


    light = None

    try:
        light = Light(18)  # Default frequency of 8kHz
    except:
        logging.info("Failed to initialize lights")

    if args.on:
        light.on()
        if args.brightness is not None:
            light.set_brightness(args.brightness)
    elif args.off:
        light.off()
    elif args.brightness is not None:
        light.on()
        light.set_brightness(args.brightness)
    elif args.log:
        brihgtness = light.get_brightness()
        logging.info(f"brightness, value={brihgtness:.2f}")
    else:
        logging.info("No action specified. Use --on, --off, or --brightness.")
