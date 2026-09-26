import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _get_bool(name, default=False):
    """Parse a truthy/falsy environment variable."""
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def _get_bool_auto(name):
    """Parse a truthy/falsy env var, returning None when it is unset.

    None means "unspecified" so callers can fall back to a value derived from
    hardware instead of forcing an explicit choice (e.g. the camera count
    implied by the detected Gardyn model).
    """
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return None
    return raw.strip().lower() in ("1", "true", "yes", "on")


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

# Per-model hardware profiles (issues #72, #84) live in app/lib/models.py as
# Gardyn model classes with shared defaults on a base Gardyn. The env vars
# above still take precedence at runtime: SENSOR_TYPE picks the temp/humidity
# driver, an explicit LOWER_CAMERA_ENABLED overrides the model's camera
# layout, and GARDYN_MODEL forces the model instead of auto-detecting it.

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

# Longest single pump run, in seconds. 900 (15 minutes) follows the Gardyn and
# pump-vendor guidance the water CLI was built on. Defined here so the schedule
# compiler can clamp to it; the REST, MQTT and CLI paths enforce it in the pump PR.
MAX_PUMP_RUN_SECONDS = _get_int("MAX_PUMP_RUN_SECONDS", 900)

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

# Tank geometry for the cm->gallons readout: distance (cm) from the sensor to the
# water surface when the tank is full vs empty, and the tank capacity in gallons
# (Gardyn Home ~5 gal, Studio ~4 gal). Calibrate FULL/EMPTY to your unit.
WATER_FULL_CM = _get_float("WATER_FULL_CM", 5)
WATER_EMPTY_CM = _get_float("WATER_EMPTY_CM", 20)
TANK_CAPACITY_GALLONS = _get_float("TANK_CAPACITY_GALLONS", 5)

# How often (seconds) the MQTT service re-reads the tank and refreshes the
# low-water alert. Kept short so a transient false alarm self-clears quickly.
WATER_CHECK_SECONDS = _get_int("WATER_CHECK_SECONDS", 180)

# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------
# Whether this unit has a lower camera. Unset means "follow the detected model
# profile": the Gardyn 3.0 ships with the upper camera only. Set
# LOWER_CAMERA_ENABLED=true/false in .env for units that differ from their
# profile (the simulator sets it true to keep both cameras). Resolve it through
# app/lib/hardware.lower_camera_enabled().
LOWER_CAMERA_ENABLED = _get_bool_auto("LOWER_CAMERA_ENABLED")
UPPER_CAMERA_DEVICE = os.getenv("UPPER_CAMERA_DEVICE", "/dev/video0")
LOWER_CAMERA_DEVICE = os.getenv("LOWER_CAMERA_DEVICE", "/dev/video2")
UPPER_IMAGE_PATH = os.getenv("UPPER_IMAGE_PATH", "/tmp/upper_camera.jpg")
LOWER_IMAGE_PATH = os.getenv("LOWER_IMAGE_PATH", "/tmp/lower_camera.jpg")
CAMERA_RESOLUTION = os.getenv("CAMERA_RESOLUTION", "640x480")
# Rotate the upper camera at capture time (right angles: 0, 90, 180, 270). The
# module is mounted sideways in the enclosure, so the default is 90, which
# fswebcam applies clockwise; use 270 for counter-clockwise and 0 to disable.
# Rotating in fswebcam keeps the web UI, MQTT image entity, and timelapse frames
# consistently oriented.
UPPER_CAMERA_ROTATE = _get_int("UPPER_CAMERA_ROTATE", 90)
IMAGE_INTERVAL_SECONDS = _get_int("IMAGE_INTERVAL_SECONDS", 3600)

# Timelapse: archive a timestamped frame on each capture, capped at MAX_FRAMES,
# and assemble into mp4 at TIMELAPSE_FPS. Stored under the repo by default.
TIMELAPSE_DIR = os.getenv(
    "TIMELAPSE_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "timelapse")
)
TIMELAPSE_MAX_FRAMES = _get_int("TIMELAPSE_MAX_FRAMES", 720)
TIMELAPSE_FPS = _get_int("TIMELAPSE_FPS", 12)

# ---------------------------------------------------------------------------
# REST API auth (optional). When GARDEN_ADMIN_PASSWORD is set, non-localhost
# requests must send it via the X-API-Key header. Localhost (cron) bypasses.
# We trim surrounding whitespace so values stored in .env or copied by hand do
# not fail unexpectedly.
#
# GARDEN_API_KEY is the deprecated name for this same value. It is still
# honoured as a fallback on purpose: an empty password disables the auth hook
# entirely (see app/__init__.py), so a rename that missed a .env file would
# silently reopen the API on the network instead of erroring. The fallback
# keeps that failure loud (app logs a deprecation warning) rather than quiet.
# ---------------------------------------------------------------------------
GARDEN_ADMIN_PASSWORD = (
    os.getenv("GARDEN_ADMIN_PASSWORD") or os.getenv("GARDEN_API_KEY") or ""
).strip()

# ---------------------------------------------------------------------------
# State persistence (actuator + grow-cycle state, for power-loss recovery)
# ---------------------------------------------------------------------------
STATE_FILE = os.path.expanduser(os.getenv("STATE_FILE", "~/.garden_state.json"))
SCHEDULE_FILE = os.path.expanduser(os.getenv("SCHEDULE_FILE", "~/.garden_schedule.json"))

# Per-pod plant tracking (name + shape code). POD_COUNT pods (Gardyn Home = 30).
POD_COUNT = _get_int("POD_COUNT", 30)
# Tower geometry, so the UI can organise pods the way the unit is actually
# built rather than as a flat 1..N list. POD_COLUMNS is how many vertical pod
# columns the unit has; pods fill down the first column, then the second, and
# so on. POD_SIDE_PATTERN lists the side each pod sticks out on, ordered from
# the highest pod down ("l" or "r"), and every column shares that pattern.
# Leaving POD_COLUMNS at 1 renders a single flat column, which is what a unit
# with no known geometry gets.
POD_COLUMNS = _get_int("POD_COLUMNS", 1)
POD_SIDE_PATTERN = os.getenv("POD_SIDE_PATTERN", "").strip().lower()
PODS_FILE = os.path.expanduser(os.getenv("PODS_FILE", "~/.garden_pods.json"))

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

# Groq advice integration -- see app/integrations/groq.py.
# This is an OUTBOUND credential and is unrelated to GARDEN_ADMIN_PASSWORD,
# which authenticates inbound REST calls. Never reuse one for the other.
# The integration stays inert (is_enabled() -> False) until a key is set.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
# qwen/qwen3.8-27b is the only current Groq model that takes image input, which
# this integration needs for the camera frame. The free plan allows 30 requests
# per minute and 1000 per day; note each image counts as 2048 input tokens
# against an 8K tokens-per-minute ceiling, so a handful of image calls a minute
# is the practical limit. Override for a text-only, cheaper model if you do not
# want the photo, e.g. openai/gpt-oss-20b.
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
# The free plan enforces an output-tokens-per-minute (OTPM) ceiling of 1000 and
# rejects any request whose *requested* max output exceeds it, with a 429
# before the model runs. 1024 therefore fails on a free key; 800 leaves headroom
# and still fits a full answer. Raise it only on a paid tier.
GROQ_MAX_TOKENS = _get_int("GROQ_MAX_TOKENS", 800)
# A round trip normally takes a few seconds; fail fast rather than let a
# request hang against Waitress's worker threads.
GROQ_TIMEOUT = _get_int("GROQ_TIMEOUT", 30)
