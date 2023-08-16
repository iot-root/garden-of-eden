#coding=utf-8
import pigpio
import time

from .config import CHANNEL_LED, FREQ_LED

class LED:
    # 0 => off
    # 1 => on
    LIGHT_STATUS = 0
    LIGHT_DUTY = 0
    DUTY_INTERVAL = 10
    MIN_DUTY = 0
    MAX_DUTY = 255
    HALF_DUTY = 128
    INTERRUPT = False

    def __init__(self, init_status = 0):
        self.pwm = pigpio.pi()

    def start(self):
        print('led starting')
        if not self.pwm:
            self.pwm = pigpio.pi()
        self.pwm.set_PWM_frequency(CHANNEL_LED, FREQ_LED)
        self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.MIN_DUTY)
        self.save_status(self.MIN_DUTY)


    def stop(self):
        if self.pwm:
            self.pwm.set_PWM_frequency(CHANNEL_LED, 0)
            self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.MIN_DUTY)
        print('led stopped')

    def turn_on(self):
        if not hasattr(self, 'pwm') or not self.pwm:
            self.start()
        self.LIGHT_STATUS = 1
        self.LIGHT_DUTY = self.LIGHT_STATUS * 128
        print("Changing it to {}".format(self.LIGHT_DUTY))
        self.pwm.set_PWM_frequency(CHANNEL_LED, FREQ_LED)
        self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.LIGHT_DUTY)

    def boost(self):
        if self.INTERRUPT:
            return False
        if not hasattr(self, 'pwm') or not self.pwm:
            self.start()
        self.LIGHT_STATUS = 1
        self.LIGHT_DUTY = self.LIGHT_STATUS * self.MAX_DUTY
        print("Changing it to {}".format(self.LIGHT_DUTY))
        self.pwm.set_PWM_frequency(CHANNEL_LED, FREQ_LED)
        self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.LIGHT_DUTY)

    def turn_off(self):
        if hasattr(self, 'pwm'):
            self.LIGHT_STATUS = 0
            self.LIGHT_DUTY = self.LIGHT_STATUS * 0
            print("Changing it to {}".format(self.LIGHT_DUTY))
            self.pwm.set_PWM_frequency(CHANNEL_LED, 0)
            self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.LIGHT_DUTY)
            self.stop()

    def lighter(self):
        if self.INTERRUPT:
            return False
        self.LIGHT_STATUS = 1
        self.LIGHT_DUTY = min(self.MAX_DUTY, self.LIGHT_DUTY + self.DUTY_INTERVAL)
        self.pwm.set_PWM_frequency(CHANNEL_LED, FREQ_LED)
        self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.LIGHT_DUTY)

    def dimmer(self):
        self.LIGHT_DUTY = min(self.MIN_DUTY, self.LIGHT_DUTY - self.DUTY_INTERVAL)
        if not self.LIGHT_DUTY:
            self.LIGHT_STATUS = 0
            self.pwm.set_PWM_frequency(CHANNEL_LED, self.MIN_DUTY)
        else:
            self.pwm.set_PWM_frequency(CHANNEL_LED, FREQ_LED)
        self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.LIGHT_DUTY)

    def adjust(self, percent):
        if self.INTERRUPT:
            return False
        p = int(percent)
        new_light_duty = int(p * self.MAX_DUTY / 100)
        if not hasattr(self, 'pwm') or not self.pwm:
            self.start()
        self.LIGHT_DUTY = min(max(self.MIN_DUTY, new_light_duty), self.MAX_DUTY)
        if not self.LIGHT_DUTY:
            self.turn_off()
        else:
            self.LIGHT_STATUS = 1
            self.pwm.set_PWM_frequency(CHANNEL_LED, FREQ_LED)
            self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.LIGHT_DUTY)

if __name__ == "__main__":
    led = LED()
    # Run a test if class is called directly
    try:
        print("LED On")
        led.turn_on()
        time.sleep(5)

        print("LED Boost")
        led.boost()
        time.sleep(5)

        print("LED dimmer")
        led.dimmer()
        time.sleep(5)

        print("LED adjust 50 percent")
        led.adjust(50)
        time.sleep(5)

        print("LED lighter")
        led.lighter()
        time.sleep(5)

        print("LED Off")
        led.turn_off()

    except KeyboardInterrupt:
        print("Script interrupted. Turning off the LED...")
        led.turn_off()