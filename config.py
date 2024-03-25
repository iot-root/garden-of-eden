import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MQTT configurations
BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = os.getenv("MQTT_PORT", "1883")
KEEP_ALIVE_INTERVAL = os.getenv("MQTT_KEEPALIVE_INTERVAL", "60")

# Topic configurations
BASE_TOPIC = os.getenv("MQTT_BASETOPIC", "eden")

USERNAME = os.getenv("MQTT_USERNAME", "gardyn")
PASSWORD = os.getenv("MQTT_PASSWORD", "somepassword")
