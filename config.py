import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def _get_int(name, default, minimum=None, maximum=None):
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        value = default
    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value

def _get_float(name, default, minimum=None, maximum=None):
    try:
        value = float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        value = default
    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value

# MQTT configurations
BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = _get_int("MQTT_PORT", 1883, minimum=1, maximum=65535)
KEEP_ALIVE_INTERVAL = _get_int("MQTT_KEEPALIVE_INTERVAL", 60, minimum=1)

# Topic configurations
VERSION = os.getenv("MQTT_VERSION", "1.0.0")
IDENTIFIER = os.getenv("MQTT_IDENTIFIER", "gardyn-xx")
MODEL= os.getenv("MQTT_DEVICE_MODEL", "gardyn 3.0")
BASE_TOPIC = os.getenv("MQTT_BASETOPIC", "gardyn")

USERNAME = os.getenv("MQTT_USERNAME")
PASSWORD = os.getenv("MQTT_PASSWORD")

SENSOR_TYPE = os.getenv('SENSOR_TYPE')

WATER_LOW_CM = _get_float("WATER_LOW_CM", 0, minimum=0) or None

UPPER_CAMERA_DEVICE = os.getenv("UPPER_CAMERA_DEVICE", "/dev/video0")
LOWER_CAMERA_DEVICE = os.getenv("LOWER_CAMERA_DEVICE", "/dev/video2")
UPPER_IMAGE_PATH = os.getenv("UPPER_IMAGE_PATH", "/tmp/upper_camera.jpg")
LOWER_IMAGE_PATH = os.getenv("LOWER_IMAGE_PATH", "/tmp/lower_camera.jpg")
CAMERA_RESOLUTION = os.getenv("CAMERA_RESOLUTION", "640x480")
IMAGE_INTERVAL_SECONDS = _get_int("IMAGE_INTERVAL_SECONDS", 3600, minimum=1)
