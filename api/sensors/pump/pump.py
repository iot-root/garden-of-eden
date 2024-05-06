import argparse
from gpiozero import PWMLED
from gpiozero.pins.pigpio import PiGPIOFactory
import pigpio
from time import sleep

class GPIOController:
    def __init__(self, pin, pin_factory=None):
        self.pin = pin
        self.pin_factory = pin_factory
        if self.pin_factory:
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
        
class Pump:
    def __init__(self, pin=24, frequency=50, pin_factory=None):
        # pigpiod is running on port 8888
        # Note: for docker: PiGPIOFactory(host='pigpiod', port=8888)
        self.pin = pin
        self.pin_factory = pin_factory if pin_factory else PiGPIOFactory()
        self.pump = PWMLED(self.pin, pin_factory=self.pin_factory)
        self.gpio = GPIOController(pin, self.pin_factory)
        self.set_frequency(frequency)

    def on(self):
        """
        Turn pump on. Default to 30 percent duty.
        """
        logging.info(f"Turning pump on")
        self.pump.value = 1

    def off(self):
        """
        Turn pump off.
        """
        logging.info(f"Turning pump off")
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
        logging.info(f"Setting pump frequency to {frequency}")
        self.gpio.set_frequency(frequency)

    def set_duty_cycle(self, duty_cycle_percentage):
        """
        Adjust the speed of the pump.

        Args:
        - duty_cycle_percentage (int): A value between 0 (off) and 100 (full brightness).
        """
        if 0 <= duty_cycle_percentage <= 100:
            # gpiozero's PWMLED uses a 0-1 scale for duty cycle
            duty = duty_cycle_percentage / 100.0
            logging.info(f"Setting pump duty_cycle to {duty_cycle_percentage}%")
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
        logging.info(f"Pump duty_cycle is {duty_cycle_percentage}%")
        return duty_cycle_percentage

    def close(self):
        self.pump.close()
        self.gpio.stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control a pump.')
    parser.add_argument('--on', action='store_true', help='Turn the pump on.')
    parser.add_argument('--off', action='store_true', help='Turn the pump off.')
    parser.add_argument('--speed', type=int, default=None, help='Set the pump speed (0-100).')
    parser.add_argument('--factory-host', type=str, default=None, help='GPIO factory host for remote access.')
    parser.add_argument('--factory-port', type=int, default=None, help='GPIO factory port for remote access.')


    args = parser.parse_args()

    pin_factory = None
    if args.factory_host and args.factory_port:
        pin_factory = {'host': args.factory_host, 'port': args.factory_port}

    pump = Pump(24, pin_factory=pin_factory)  # Default frequency of 50Hz

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
        logging.info("No action specified. Use --on, --off, or --speed.")