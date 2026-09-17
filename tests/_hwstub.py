"""Install fake hardware modules into ``sys.modules`` so the test suite (and
linting/import checks) run on any machine, not just a Raspberry Pi.

Imported for its side effects at the top of ``tests/__init__.py`` *before* any
``app`` code is imported. Each stub is permissive (MagicMock-backed) because the
unit tests patch the specific methods/values they care about.
"""

import sys
import types
from unittest.mock import MagicMock


def _module(name):
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    return mod


def install():
    # Skip if real hardware libs are present (e.g. running on a Pi).
    try:
        import board  # noqa: F401

        return
    except Exception:
        pass

    # --- Adafruit Blinka / CircuitPython ---
    board = _module("board")
    board.I2C = MagicMock(name="board.I2C")
    board.SCL = object()
    board.SDA = object()

    busio = _module("busio")
    busio.I2C = MagicMock(name="busio.I2C")

    for name, cls in (
        ("adafruit_ahtx0", "AHTx0"),
        ("adafruit_am2320", "AM2320"),
    ):
        mod = _module(name)
        setattr(mod, cls, MagicMock(name=f"{name}.{cls}"))

    # PCT2075 returns a real number so get_pcb_temperature() serializes to JSON
    # (a MagicMock .temperature would 503 on /pcb-temp).
    class _PCT2075:
        def __init__(self, *a, **k):
            self.temperature = 30.0

    pct = _module("adafruit_pct2075")
    pct.PCT2075 = _PCT2075

    # --- gpiozero ---
    # These are real (empty) classes, not MagicMocks, so tests that patch them
    # with autospec=True (e.g. test_distance) get a valid spec.
    class _PWMLED:
        def __init__(self, *a, **k):
            self.value = 0

        def close(self):
            pass

    class _DistanceSensor:
        distance = 0.0

        def __init__(self, *a, **k):
            pass

    class _Button:
        def __init__(self, *a, **k):
            self.when_pressed = None
            self.when_released = None

    gpiozero = _module("gpiozero")
    gpiozero.PWMLED = _PWMLED
    gpiozero.DistanceSensor = _DistanceSensor
    gpiozero.Button = _Button

    pins = _module("gpiozero.pins")
    pins_pigpio = _module("gpiozero.pins.pigpio")
    pins_pigpio.PiGPIOFactory = MagicMock(name="PiGPIOFactory")
    gpiozero.pins = pins
    pins.pigpio = pins_pigpio

    # --- pigpio ---
    pigpio = _module("pigpio")
    pigpio.pi = MagicMock(name="pigpio.pi")

    # --- smbus --- (real fake so device-presence checks return cleanly)
    class _SMBus:
        def __init__(self, *a, **k):
            pass

        def read_byte_data(self, addr, reg):
            return 0

        def close(self):
            pass

    smbus = _module("smbus")
    smbus.SMBus = _SMBus

    # --- pi-ina219 --- (return real numbers so /pump/stats serializes to JSON)
    class _INA219:
        def __init__(self, *a, **k):
            pass

        def configure(self, *a, **k):
            pass

        def voltage(self):
            return 12.0

        def current(self):
            return 150.0

        def power(self):
            return 1800.0

        def shunt_voltage(self):
            return 0.01

    class DeviceRangeError(Exception):
        pass

    ina219 = _module("ina219")
    ina219.INA219 = _INA219
    ina219.DeviceRangeError = DeviceRangeError
