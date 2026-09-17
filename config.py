import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _get_bool(name, default=False):
    """Parse a truthy/falsy environment variable."""
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def _get_int(name, default):
    """Parse an int env var, accepting decimal ("72") or hex ("0x48")."""
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    raw = raw.strip()
    try:
        # base 0 auto-detects 0x/0o/0b prefixes; plain decimal also works.
        return int(raw, 0)
    except ValueError:
        return int(raw)


def _get_float(name, default):
    return float(os.getenv(name, str(default)))


# ---------------------------------------------------------------------------
# MQTT configuration
# ---------------------------------------------------------------------------
BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = _get_int("MQTT_PORT", 1883)
KEEP_ALIVE_INTERVAL = _get_int("MQTT_KEEPALIVE_INTERVAL", 60)

# Topic / device identity (used for Home Assistant discovery)
VERSION = os.getenv("MQTT_VERSION", "1.0.0")
IDENTIFIER = os.getenv("MQTT_IDENTIFIER", "gardyn-xx")
MODEL = os.getenv("MQTT_DEVICE_MODEL", "gardyn 3.0")
BASE_TOPIC = os.getenv("MQTT_BASETOPIC", "gardyn")

USERNAME = os.getenv("MQTT_USERNAME")
PASSWORD = os.getenv("MQTT_PASSWORD")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "gardyn.log")

# ---------------------------------------------------------------------------
# pigpio connection (PiGPIOFactory). For Docker, point at the pigpiod
# container, e.g. PIGPIO_HOST=pigpiod PIGPIO_PORT=8888.
# ---------------------------------------------------------------------------
PIGPIO_HOST = os.getenv("PIGPIO_HOST") or None
PIGPIO_PORT = _get_int("PIGPIO_PORT", 8888)

# ---------------------------------------------------------------------------
# Sensor / hardware model
# SENSOR_TYPE is the temp/humidity chip: "AM2320" (Gardyn 1.0/2.0) or
# "DHT20" (Gardyn 3.0+). MODEL_OVERRIDE forces a Gardyn model instead of
# auto-detecting at runtime (see app/lib/hardware.py).
# ---------------------------------------------------------------------------
SENSOR_TYPE = os.getenv("SENSOR_TYPE")
MODEL_OVERRIDE = os.getenv("GARDYN_MODEL") or None

# Per-model hardware profiles (issues #72, #84). Differences between Gardyn
# generations are captured here so detection/UX can adapt. Pin defaults still
# come from the env vars above; this table documents expected sensors and any
# known per-model deviations (extend as hardware is characterized).
MODELS = {
    "gardyn 1.0": {"temp_humidity": "AM2320", "cameras": 2},
    "gardyn 2.0": {"temp_humidity": "AM2320", "cameras": 2},
    "gardyn 3.0": {"temp_humidity": "DHT20", "cameras": 2},
    "gardyn studio": {"temp_humidity": "DHT20", "cameras": 2},
}

# ---------------------------------------------------------------------------
# GPIO pin assignments (BCM numbering)
# ---------------------------------------------------------------------------
LIGHT_PIN = _get_int("LIGHT_PIN", 18)
LIGHT_FREQUENCY = _get_int("LIGHT_FREQUENCY", 8000)

PUMP_PIN = _get_int("PUMP_PIN", 24)
PUMP_FREQUENCY = _get_int("PUMP_FREQUENCY", 50)

DISTANCE_ECHO_PIN = _get_int("DISTANCE_ECHO_PIN", 19)
DISTANCE_TRIGGER_PIN = _get_int("DISTANCE_TRIGGER_PIN", 26)

BUTTON_PIN = _get_int("BUTTON_PIN", 13)
OVER_TEMP_ALERT_PIN = _get_int("OVER_TEMP_ALERT_PIN", 25)

# Default actuator levels applied when toggled on
DEFAULT_BRIGHTNESS = _get_int("DEFAULT_BRIGHTNESS", 50)
DEFAULT_PUMP_SPEED = _get_int("DEFAULT_PUMP_SPEED", 100)

# ---------------------------------------------------------------------------
# I2C device addresses
# ---------------------------------------------------------------------------
PCB_TEMP_ADDRESS = _get_int("PCB_TEMP_ADDRESS", 0x48)
INA219_ADDRESS = _get_int("INA219_ADDRESS", 0x40)

# Over-temperature thresholds for the PCB sensor (deg C)
OVER_TEMP_HIGH = _get_float("OVER_TEMP_HIGH", 36)
OVER_TEMP_HYSTERESIS = _get_float("OVER_TEMP_HYSTERESIS", 34)

# ---------------------------------------------------------------------------
# Water level alerting
# WATER_LOW_CM is the distance (cm) from the sensor to the water surface above
# which the tank is considered low. 0/unset disables the alert.
# ---------------------------------------------------------------------------
WATER_LOW_CM = _get_float("WATER_LOW_CM", 0) or None

# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------
UPPER_CAMERA_DEVICE = os.getenv("UPPER_CAMERA_DEVICE", "/dev/video0")
LOWER_CAMERA_DEVICE = os.getenv("LOWER_CAMERA_DEVICE", "/dev/video2")
UPPER_IMAGE_PATH = os.getenv("UPPER_IMAGE_PATH", "/tmp/upper_camera.jpg")
LOWER_IMAGE_PATH = os.getenv("LOWER_IMAGE_PATH", "/tmp/lower_camera.jpg")
CAMERA_RESOLUTION = os.getenv("CAMERA_RESOLUTION", "640x480")
IMAGE_INTERVAL_SECONDS = _get_int("IMAGE_INTERVAL_SECONDS", 3600)

# ---------------------------------------------------------------------------
# REST API auth (optional). When GARDEN_API_KEY is set, non-localhost
# requests must send it via the X-API-Key header. Localhost (cron) bypasses.
# ---------------------------------------------------------------------------
GARDEN_API_KEY = os.getenv("GARDEN_API_KEY", "")

# ---------------------------------------------------------------------------
# State persistence (actuator + grow-cycle state, for power-loss recovery)
# ---------------------------------------------------------------------------
STATE_FILE = os.path.expanduser(os.getenv("STATE_FILE", "~/.garden_state.json"))
SCHEDULE_FILE = os.path.expanduser(os.getenv("SCHEDULE_FILE", "~/.garden_schedule.json"))

# ---------------------------------------------------------------------------
# Grow-cycle & notifications
# ---------------------------------------------------------------------------
GROW_STATE_FILE = os.path.expanduser(os.getenv("GROW_STATE_FILE", "~/.garden_grow.json"))
# Days after a cycle starts to remind about each task (0 disables a reminder)
THINNING_REMINDER_DAYS = _get_int("THINNING_REMINDER_DAYS", 14)
ROOT_CHECK_REMINDER_DAYS = _get_int("ROOT_CHECK_REMINDER_DAYS", 21)
HARVEST_REMINDER_DAYS = _get_int("HARVEST_REMINDER_DAYS", 35)
# Reminder cadence (days) for adding nutrients/"food"
NUTRIENT_REMINDER_DAYS = _get_int("NUTRIENT_REMINDER_DAYS", 7)

# ---------------------------------------------------------------------------
# External integrations (scaffolded; see app/integrations/ and docs/integrations/)
# ---------------------------------------------------------------------------
ALEXA_ENABLED = _get_bool("ALEXA_ENABLED", False)

THINGSBOARD_ENABLED = _get_bool("THINGSBOARD_ENABLED", False)
THINGSBOARD_HOST = os.getenv("THINGSBOARD_HOST", "")
THINGSBOARD_TOKEN = os.getenv("THINGSBOARD_TOKEN", "")

TELEGRAF_ENABLED = _get_bool("TELEGRAF_ENABLED", False)
