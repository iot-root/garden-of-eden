"""Realistic, stateful fake hardware for off-Pi simulation.

Unlike the test stubs (tests/_hwstub.py, which are bare MagicMocks for unit
tests), these fakes behave like the real devices so the web UI and Home
Assistant feel alive:

- Actuators (PWMLED) remember their value, so brightness/speed reads reflect
  what you set.
- The distance sensor oscillates slowly through the low-water threshold so you
  can watch the alert toggle.
- Temp/humidity/PCB/power sensors return believable values with light noise.
"""

import math
import sys
import time
import types

_START = time.time()


def _noise(amplitude):
    # Deterministic-ish wobble without random (keeps logs stable-ish).
    t = time.time() - _START
    return amplitude * math.sin(t / 7.0)


class FakePWMLED:
    """Mimics gpiozero.PWMLED; remembers its 0..1 value."""

    def __init__(self, pin, pin_factory=None):
        self.pin = pin
        self.value = 0.0

    def close(self):
        self.value = 0.0


class FakeDistanceSensor:
    def __init__(self, *args, echo=None, trigger=None, pin_factory=None, **kwargs):
        pass

    @property
    def distance(self):
        # Metres. Oscillate 4..12 cm over a ~2 min period so the low-water
        # alert (default 11 cm) trips and clears for testing.
        t = time.time() - _START
        cm = 8 + 4 * math.sin(t / 120.0)
        return cm / 100.0


class FakeButton:
    def __init__(self, *args, **kwargs):
        self.when_pressed = None
        self.when_held = None
        self.when_released = None


class FakePiGPIOFactory:
    def __init__(self, *args, **kwargs):
        pass


class _FakePiGPIO:
    connected = True

    def set_PWM_frequency(self, pin, frequency):
        return frequency

    def stop(self):
        pass


class _FakeTempHumidity:
    def __init__(self, *args, **kwargs):
        pass

    @property
    def temperature(self):
        return round(22.0 + _noise(1.5), 2)

    @property
    def relative_humidity(self):
        return round(55.0 + _noise(5.0), 2)


class _FakePCT2075:
    def __init__(self, *args, **kwargs):
        pass

    @property
    def temperature(self):
        return round(30.0 + _noise(1.0), 2)


class _FakeSMBus:
    def __init__(self, *args, **kwargs):
        pass

    def read_byte_data(self, addr, reg):
        return 0  # any device "present"

    def close(self):
        pass


class _FakeINA219:
    def __init__(self, *args, **kwargs):
        pass

    def configure(self, *args, **kwargs):
        pass

    def voltage(self):
        return round(12.0 + _noise(0.2), 3)

    def current(self):
        return round(150.0 + _noise(15.0), 2)

    def power(self):
        return round(1800.0 + _noise(80.0), 2)

    def shunt_voltage(self):
        return round(0.012 + _noise(0.001), 4)


class _DeviceRangeError(Exception):
    pass


def _module(name):
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    return mod


def install():
    """Inject the fakes into sys.modules. Call before importing ``app``."""
    board = _module("board")
    board.I2C = lambda *a, **k: object()
    board.SCL = object()
    board.SDA = object()

    busio = _module("busio")
    busio.I2C = lambda *a, **k: object()

    ahtx0 = _module("adafruit_ahtx0")
    ahtx0.AHTx0 = _FakeTempHumidity
    am2320 = _module("adafruit_am2320")
    am2320.AM2320 = _FakeTempHumidity
    pct = _module("adafruit_pct2075")
    pct.PCT2075 = _FakePCT2075

    gpiozero = _module("gpiozero")
    gpiozero.PWMLED = FakePWMLED
    gpiozero.DistanceSensor = FakeDistanceSensor
    gpiozero.Button = FakeButton

    pins = _module("gpiozero.pins")
    pins_pigpio = _module("gpiozero.pins.pigpio")
    pins_pigpio.PiGPIOFactory = FakePiGPIOFactory
    gpiozero.pins = pins
    pins.pigpio = pins_pigpio

    pigpio = _module("pigpio")
    pigpio.pi = lambda *a, **k: _FakePiGPIO()

    smbus = _module("smbus")
    smbus.SMBus = _FakeSMBus

    ina219 = _module("ina219")
    ina219.INA219 = _FakeINA219
    ina219.DeviceRangeError = _DeviceRangeError
