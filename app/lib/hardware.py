"""Shared hardware helpers: a single pigpio pin factory, I2C probing, and
runtime Gardyn model detection.

Centralizing the ``PiGPIOFactory`` here means every GPIO driver (in both the
REST API and the MQTT service) talks to pigpiod through one connection instead
of opening its own (see issue #67).
"""

import logging

import config

logger = logging.getLogger(__name__)

_pin_factory = None

# Known I2C addresses and which Gardyn models expose them. Used both for
# presence checks and for inferring the hardware model at runtime (#72, #84).
PCT2075_ADDRESS = config.PCB_TEMP_ADDRESS  # PCB temperature (all models)
INA219_ADDRESS = config.INA219_ADDRESS  # pump power monitor
DHT20_ADDRESS = 0x38  # temp/humidity on Gardyn 3.0+
AM2320_ADDRESS = 0x5C  # temp/humidity on Gardyn 1.0/2.0


def get_pin_factory():
    """Return a process-wide shared PiGPIOFactory.

    Honors ``PIGPIO_HOST``/``PIGPIO_PORT`` so the same code runs natively on the
    Pi (local pigpiod) or in Docker (remote pigpiod container). Returns ``None``
    if pigpio is unavailable so callers can degrade gracefully off-Pi.
    """
    global _pin_factory
    if _pin_factory is not None:
        return _pin_factory

    try:
        from gpiozero.pins.pigpio import PiGPIOFactory

        if config.PIGPIO_HOST:
            logger.info(
                "Creating shared PiGPIOFactory(host=%s, port=%s)",
                config.PIGPIO_HOST,
                config.PIGPIO_PORT,
            )
            _pin_factory = PiGPIOFactory(host=config.PIGPIO_HOST, port=config.PIGPIO_PORT)
        else:
            logger.info("Creating shared local PiGPIOFactory")
            _pin_factory = PiGPIOFactory()
    except Exception as exc:  # pragma: no cover - hardware/daemon dependent
        logger.error("Could not initialize PiGPIOFactory: %s", exc)
        _pin_factory = None

    return _pin_factory


def i2c_device_present(address):
    """Return True if an I2C device ACKs at ``address`` on bus 1."""
    try:
        import smbus

        bus = smbus.SMBus(1)
        try:
            bus.read_byte_data(address, 0)
            return True
        finally:
            bus.close()
    except Exception:
        return False


def detect_model():
    """Best-effort Gardyn model inference.

    Returns a string like ``"gardyn 3.0"``. ``GARDYN_MODEL`` (config
    ``MODEL_OVERRIDE``) short-circuits detection. Falls back to the configured
    ``MODEL`` when hardware can't be probed (e.g. off-Pi).
    """
    if config.MODEL_OVERRIDE:
        return config.MODEL_OVERRIDE

    # The temp/humidity chip distinguishes generations: DHT20 -> 3.0+,
    # AM2320 -> 1.0/2.0. AM2320 needs a wakeup and won't always ACK, so we
    # also fall back to the configured SENSOR_TYPE.
    if i2c_device_present(DHT20_ADDRESS) or config.SENSOR_TYPE == "DHT20":
        return "gardyn 3.0"
    if config.SENSOR_TYPE == "AM2320":
        return "gardyn 2.0"
    return config.MODEL
