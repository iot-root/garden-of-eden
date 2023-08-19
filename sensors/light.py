from gpiozero import PWMLED
from gpiozero.pins.pigpio import PiGPIOFactory
import pigpio
from time import sleep

class Light:
    def __init__(self, pin, frequency=8000):
        # pigpiod is running on port 8888
        # self.factory = PiGPIOFactory(host='pigpiod', port=8888)  # Specify the address and port
        self.factory = PiGPIOFactory()
        self.pin = pin
        self.led = PWMLED(self.pin, pin_factory=self.factory)
        self.pi = pigpio.pi()
        self.set_frequency(frequency)

    def on(self):
        self.led.value = 1

    def off(self):
        self.led.value = 0

    def adjust(self, brightness):
        """Adjust the brightness of the light.

        Args:
        - brightness (float): A value between 0 (off) and 1 (full brightness).
        """
        if 0 <= brightness <= 1:
            self.led.value = brightness
        else:
            raise ValueError("Brightness must be between 0 and 1")

    def set_frequency(self, frequency):
        self.pi.set_PWM_frequency(self.pin, frequency)

    def close(self):
        self.led.close()
        self.pi.stop()

if __name__ == '__main__':
    # Usage example:
    light = Light(18)  # Default frequency of 8kHz
    light.on()
    light.adjust(0.5)  # Adjust to 50% brightness
    sleep(3)
    light.off()
    light.close()
