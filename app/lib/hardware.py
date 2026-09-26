"""Shared hardware helpers: a single pigpio pin factory, I2C probing, and
runtime Gardyn model detection.

Centralizing the ``PiGPIOFactory`` here means every GPIO driver (in both the
REST API and the MQTT service) talks to pigpiod through one connection instead
of opening its own (see issue #67).
"""

import logging

import config
from app.lib.models import profile_for  # re-exported for the /system route

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


class GPIOController:
    """Thin pigpiod client for PWM frequency control on a single pin.

    Shared by the light and pump drivers, which previously each carried a
    copy-pasted copy of this class — the same single-connection goal as the
    shared pin factory above (issue #67). ``pi_factory`` is injectable so
    tests can substitute ``pigpio.pi``; when omitted the real client is
    imported lazily.
    """

    def __init__(self, pin, pin_factory=None, pi_factory=None):
        if pi_factory is None:
            import pigpio

            pi_factory = pigpio.pi
        self.pin = pin
        self.pin_factory = pin_factory
        if config.PIGPIO_HOST:
            self.pi = pi_factory(config.PIGPIO_HOST, config.PIGPIO_PORT)
        else:
            self.pi = pi_factory()

        if not self.pi.connected:
            raise RuntimeError(
                "Failed to connect to pigpiod daemon. Ensure it's running and accessible."
            )

    def set_frequency(self, frequency):
        if self.pi:
            self.pi.set_PWM_frequency(self.pin, frequency)
        else:
            raise RuntimeError("pigpio.pi client is not initialized.")


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
    """Best-effort Gardyn model resolution.

    Returns a string like ``"gardyn studio"``. A model chosen in the web UI
    wins, then ``GARDYN_MODEL`` (config ``MODEL_OVERRIDE``), then inference
    from the temp/humidity chip, then the configured ``MODEL`` when hardware
    can't be probed (e.g. off-Pi). The UI choice is read per call, so changing
    it takes effect without a restart.
    """
    # Imported here rather than at module scope: settings imports models, and
    # hardware is imported by that same path.
    from app.lib.settings import get_model_override

    chosen = get_model_override()
    if chosen:
        return chosen
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


def lower_camera_enabled(model=None):
    """Return True when this unit has a lower camera.

    An explicit ``LOWER_CAMERA_ENABLED`` in the environment always wins; when it
    is unset the model profile decides, so a Studio reports the upper camera
    only without any manual configuration. Unknown models keep both cameras.
    """
    if config.LOWER_CAMERA_ENABLED is not None:
        return config.LOWER_CAMERA_ENABLED
    profile = profile_for(model if model is not None else detect_model())
    return bool(profile.get("lower_camera", True))


def pod_capacity(model=None):
    """Total number of plant pods on this unit.

    ``POD_COUNT`` in the environment wins when set, otherwise the model
    profile decides: a Studio has 16, a Home has 30.
    """
    if config.POD_COUNT:
        return int(config.POD_COUNT)
    profile = profile_for(model if model is not None else detect_model())
    return int(profile.get("pods", 30))


def tower_count(model=None):
    """Number of pod towers/columns on this unit.

    ``POD_COLUMNS`` in the environment wins when set, otherwise the model
    profile decides: a Studio has 2, a Home has 3.
    """
    if config.POD_COLUMNS:
        return int(config.POD_COLUMNS)
    profile = profile_for(model if model is not None else detect_model())
    return int(profile.get("towers", 3))
