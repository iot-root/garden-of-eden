import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MQTT configurations
BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = int(os.getenv("MQTT_PORT", "1883"))
KEEP_ALIVE_INTERVAL = int(os.getenv("MQTT_KEEPALIVE_INTERVAL", "60"))

# Topic configurations
BASE_TOPIC = os.getenv("MQTT_BASETOPIC", "gardyn")

USERNAME = os.getenv("MQTT_USERNAME")
PASSWORD = os.getenv("MQTT_PASSWORD")
