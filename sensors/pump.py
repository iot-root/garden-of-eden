# coding=utf-8
import RPi.GPIO as GPIO
import time
import os

from config import CHANNEL_WATER_PUMP, FREQ_WATER_PUMP, MAX_DUTY_PUMP, INIT_DUTY_WATER_PUMP, LAST_SECS_WATER_PUMP

class Pump:
    PUMP_STATUS = 0
    def __init__(self):
        if not GPIO.getmode():
            GPIO.setmode(GPIO.BCM)
        self.started = False

    def clear(self):
        self.stop()
        GPIO.cleanup(CHANNEL_WATER_PUMP)
        print('Water Pump stopped at channel {}, GPIO has been cleaned up'.format(CHANNEL_WATER_PUMP))
        print('----------------------------------------')
        # read_ina219()

    def turn_off(self):
        self.start_time = int(time.time())
        self.last_sec = 0
        self.started = False
        if self.pwm:
            self.pwm.ChangeDutyCycle(0)
            self.pwm.stop()
        GPIO.cleanup(CHANNEL_WATER_PUMP)
        self.pwm = None
        self.PUMP_STATUS = 0

    def turn_on(self):
        # read_ina219()
        if not hasattr(self, 'pwm') or not self.pwm:
            GPIO.setup(CHANNEL_WATER_PUMP, GPIO.OUT)
            self.pwm = GPIO.PWM(CHANNEL_WATER_PUMP, FREQ_WATER_PUMP)

        duty = INIT_DUTY_WATER_PUMP
        if not self.started:
            self.pwm.start(duty)
            self.started = True
            self.PUMP_STATUS = 1

        print('Water Pump started at channel {}'.format(CHANNEL_WATER_PUMP))
        increasing = True
        try:
            while self.started and duty < MAX_DUTY_PUMP:
                if duty == MAX_DUTY_PUMP:
                    increasing = False
                elif duty == 0:
                    increasing = True
                if increasing:
                    duty += 10
                    self.pwm.ChangeDutyCycle(duty)
                time.sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    pump = Pump()

    try:
        print("Pump On")
        pump.turn_on()
        time.sleep(5)

        print("Pump Off")
        pump.turn_off()
    except KeyboardInterrupt:
        print("Script interrupted. Turning off the Pump")
        pump.turn_off()