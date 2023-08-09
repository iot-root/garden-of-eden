# coding=utf-8
import RPi.GPIO as GPIO
import time
from config import CHANNEL_WATER_LVL_IN, CHANNEL_WATER_LVL_OUT, TIMEOUT_WATER_LVL

class WaterLevel:
    def __init__(self):
        if not GPIO.getmode():
            GPIO.setmode(GPIO.BCM)     # Numbers GPIOs by GPIO pin, not physical location
        GPIO.setup(CHANNEL_WATER_LVL_OUT, GPIO.OUT)
        GPIO.setup(CHANNEL_WATER_LVL_IN, GPIO.IN)
        GPIO.output(CHANNEL_WATER_LVL_OUT, GPIO.LOW)
        print('Waiting 5s For Sensor To Settle')
        time.sleep(5)

    def measure_once(self):
        GPIO.output(CHANNEL_WATER_LVL_OUT, GPIO.HIGH)
        time.sleep(.00003)
        GPIO.output(CHANNEL_WATER_LVL_OUT, GPIO.LOW)
        timeout = time.time() + TIMEOUT_WATER_LVL

        while GPIO.input(CHANNEL_WATER_LVL_IN) == GPIO.LOW and timeout > time.time():
            pulse_start = time.time()

        while GPIO.input(CHANNEL_WATER_LVL_IN) == GPIO.HIGH and timeout > time.time():
            pulse_end = time.time()

        if timeout < time.time():
            raise Exception('Water level measurement timeout.')

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        print('[{}] - Water Level Distance: {} cm'.format(time.ctime(time.time()), distance))
        return distance

    def measure(self):
        m = []
        for i in range(10):
            try:
                d = self.measure_once()
                m.append(d)
            except:
                pass
        l = self.median(m)
        return round(sum(l) / len(l), 2)

    def median(d):
        if type(d) != list:
            return ''
        s = sorted(d)
        l = len(d)
        return s[(int(l / 2)) : (int(l / 2) + 1)] if l % 2 > 0 else s[(int(l / 2) - 1) : (int(l / 2) + 1)]

if __name__ == "__main__":
    waterlevel = WaterLevel()

    try:
        print("Measuring waterlevel:")
        height = waterlevel.measure()
        print("Level is:")
        print(height)

    except KeyboardInterrupt:
        print("Script interrupted.")