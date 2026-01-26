import subprocess
import threading
from threading import Timer
import signal
import logging
from logging.handlers import RotatingFileHandler
import paho.mqtt.client as mqtt
import base64
import os
import sqlite3
import time
import json
# import picamera
# import cv2
from time import sleep
from config import USERNAME, PASSWORD, BROKER, PORT, KEEP_ALIVE_INTERVAL, BASE_TOPIC, IDENTIFIER, MODEL, VERSION, WATER_LOW_CM, UPPER_CAMERA_DEVICE, LOWER_CAMERA_DEVICE, UPPER_IMAGE_PATH, LOWER_IMAGE_PATH, CAMERA_RESOLUTION, IMAGE_INTERVAL_SECONDS, LOG_LEVEL, PUBLISH_FREQUENCY_MINUTES

from gpiozero import Button  # Import gpiozero Button
from gpiozero.pins.pigpio import PiGPIOFactory

from app.sensors.light.light import Light
from app.sensors.pump.pump import Pump
from app.sensors.pcb_temp.pcb_temp import get_pcb_temperature
from app.sensors.temperature.temperature import temperature_sensor
from app.sensors.humidity.humidity import humidity_sensor
from app.sensors.distance.distance import Distance, MeasurementError

# Module globals for runtime control
client = None
stop_event = threading.Event()

# Configure logging
log_path = os.path.join(os.path.dirname(__file__), "gardyn.log")
log_level = getattr(logging, (LOG_LEVEL or "INFO").upper(), logging.INFO)

# Formatter
_LOG_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(_LOG_FMT)

# Ensure logfile can be created; fall back to console/journal if not
file_handler = None
try:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    # touch file
    with open(log_path, 'a', encoding='utf-8'):
        pass
    file_handler = RotatingFileHandler(log_path, mode='a', maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    file_handler.setFormatter(formatter)
except Exception as _e:
    import sys
    print(f"WARNING: cannot open log file {log_path}: {_e}", file=sys.stderr)

# Stream handler (always present)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Configure root logger explicitly to avoid other libs pre-configuring logging
root = logging.getLogger()
for h in list(root.handlers):
    root.removeHandler(h)
root.setLevel(log_level)
if file_handler:
    root.addHandler(file_handler)
root.addHandler(stream_handler)

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")

# Persistent publish queue (SQLite)
QUEUE_DB = os.path.join(os.path.dirname(__file__), "gardyn_pubqueue.db")
_queue_lock = threading.Lock()

def _init_queue_db():
    conn = sqlite3.connect(QUEUE_DB, check_same_thread=False)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS publish_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            payload_b64 TEXT NOT NULL,
            qos INTEGER NOT NULL,
            retain INTEGER NOT NULL,
            is_binary INTEGER NOT NULL,
            created_at INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    return conn

_queue_conn = _init_queue_db()

def enqueue_message(topic, payload, qos=0, retain=False):
    try:
        is_binary = 1 if isinstance(payload, (bytes, bytearray)) else 0
        if is_binary:
            payload_b64 = base64.b64encode(payload).decode("ascii")
        else:
            payload_b64 = base64.b64encode(str(payload).encode("utf-8")).decode("ascii")
        with _queue_lock:
            c = _queue_conn.cursor()
            c.execute(
                "INSERT INTO publish_queue (topic, payload_b64, qos, retain, is_binary, created_at) VALUES (?,?,?,?,?,?)",
                (topic, payload_b64, int(qos), int(bool(retain)), is_binary, int(time.time())),
            )
            _queue_conn.commit()
    except Exception:
        logger.exception("Failed to enqueue message to persistent queue")

def _get_queued_messages():
    with _queue_lock:
        c = _queue_conn.cursor()
        c.execute("SELECT id, topic, payload_b64, qos, retain, is_binary FROM publish_queue ORDER BY id ASC")
        return c.fetchall()

def _delete_queued_message(msg_id):
    with _queue_lock:
        c = _queue_conn.cursor()
        c.execute("DELETE FROM publish_queue WHERE id = ?", (msg_id,))
        _queue_conn.commit()

def flush_queue(client):
    rows = _get_queued_messages()
    for row in rows:
        msg_id, topic, payload_b64, qos, retain, is_binary = row
        try:
            raw = base64.b64decode(payload_b64)
            payload = raw if is_binary else raw.decode("utf-8")
            client.publish(topic, payload, qos=qos, retain=bool(retain))
            _delete_queued_message(msg_id)
        except Exception:
            logger.exception("Failed to publish queued message; will retry later")
            break

def safe_publish(topic, payload, qos=0, retain=False):
    """Publish immediately if connected, otherwise persist to disk for later flush."""
    try:
        if client and getattr(client, "is_connected", lambda: False)():
            try:
                return client.publish(topic, payload, qos=qos, retain=retain)
            except Exception:
                logger.exception("Publish failed, enqueueing message")
                enqueue_message(topic, payload, qos=qos, retain=retain)
                return None
        else:
            enqueue_message(topic, payload, qos=qos, retain=retain)
            return None
    except Exception:
        logger.exception("Unexpected error in safe_publish; enqueueing")
        enqueue_message(topic, payload, qos=qos, retain=retain)
        return None

# Initialize devices
pin_factory = PiGPIOFactory()

pump = Pump(pin_factory=pin_factory)
light = Light(pin_factory=pin_factory)
distance_sensor = Distance(pin_factory=pin_factory)

# default on brightness
brightness  = 50
speed       = 100
# publish_frequency comes from config (minutes -> seconds)
try:
    publish_frequency = int(PUBLISH_FREQUENCY_MINUTES) * 60
except Exception:
    publish_frequency = 30 * 60

# Button GPIO setup using gpiozero
button_pin = 13
button = Button(button_pin, pin_factory=pin_factory, bounce_time=0.2, hold_time=2)  # hold_time = 2 seconds for long press detection

# Variables to track the state of the light and pump
light_state = False
pump_state = False
double_press_time = 1  # Time to detect a double press (in seconds)
press_count = 0
double_press_timer = None

# Button press callbacks
def toggle_light():
    global light_state
    light_state = not light_state
    if light_state:
        logger.info("Toggling Light ON")
        light.set_duty_cycle(brightness)
        if client:
            safe_publish(BASE_TOPIC + "/light/state", "ON")
        else:
            logger.warning("Client not ready; skipping publish for light ON")
    else:
        logger.info("Toggling Light OFF")
        light.off()
        if client:
            safe_publish(BASE_TOPIC + "/light/state", "OFF")
        else:
            logger.warning("Client not ready; skipping publish for light OFF")

def toggle_pump():
    global pump_state
    pump_state = not pump_state
    if pump_state:
        logger.info("Toggling Pump ON")
        pump.set_speed(speed)
        if client:
            safe_publish(BASE_TOPIC + "/pump/state", "ON")
        else:
            logger.warning("Client not ready; skipping publish for pump ON")
    else:
        logger.info("Toggling Pump OFF")
        pump.off()
        if client:
            safe_publish(BASE_TOPIC + "/pump/state", "OFF")
        else:
            logger.warning("Client not ready; skipping publish for pump OFF")

def handle_button_press():
    global press_count, double_press_timer

    press_count += 1

    if press_count == 1:
        # Start a timer to detect if a second press occurs within the double press time window
        double_press_timer = Timer(double_press_time, handle_single_press)
        double_press_timer.start()
    elif press_count == 2:
        # If a second press occurs, cancel the single press action and trigger the double press action
        if double_press_timer:
            double_press_timer.cancel()
        handle_double_press()
        press_count = 0

def handle_single_press():
    global press_count
    toggle_light()  # Single press toggles the light
    press_count = 0

def handle_double_press():
    toggle_pump()  # Double press toggles the pump

# Set button event for press detection
button.when_pressed = handle_button_press

# helpers
def flash_lights(times=3, delay=0.3):
    original_brightness = light.get_brightness()  # Save the brightness (0–100 scale)
    was_on = original_brightness > 0  # If >0%, we consider it "on"

    logger.info(f"Flashing lights {times} times. Original brightness: {original_brightness}%")

    for _ in range(times):
        light.off()
        sleep(delay)
        light.set_brightness(100)  # Flash full brightness for maximum visibility
        sleep(delay)
    # Restore original state
    if was_on:
        light.set_brightness(original_brightness)
    else:
        light.off()

def safe_distance_measure():
    global distance_sensor
    try:
        return distance_sensor.measure_once()
    except MeasurementError as e:
        logger.warning(f"Distance measure failed: {e}, trying recovery")
        try:
            distance_sensor = Distance(pin_factory=pin_factory)
            return distance_sensor.measure_once()
        except Exception as e2:
            logger.error(f"Distance full recovery failed: {e2}")
            return None

def publish_water_low_mode(client):
    if WATER_LOW_CM not in (None, 0):
        mode = "Enabled"
    else:
        mode = "Disabled"
    logger.info(f"Publishing water low mode: {mode}")
    safe_publish(BASE_TOPIC + "/water/low/mode", mode, retain=True)


def update_water_low_state(client):
    if WATER_LOW_CM not in (None, 0):
        distance = safe_distance_measure()
        if distance is not None:
            if distance > WATER_LOW_CM:
                safe_publish(BASE_TOPIC + "/water/low/state", "ON", retain=True)
                logger.info(f"Updated water low state to ON (distance {distance:.2f}cm > {WATER_LOW_CM:.2f}cm)")
            else:
                safe_publish(BASE_TOPIC + "/water/low/state", "OFF", retain=True)
                logger.info(f"Updated water low state to OFF (distance {distance:.2f}cm <= {WATER_LOW_CM:.2f}cm)")
        else:
            logger.warning("Could not update water low state because distance reading failed")
    else:
        # If checking is disabled, maybe set it to OFF by default
        safe_publish(BASE_TOPIC + "/water/low/state", "OFF", retain=True)
        logger.info("Water low checking disabled, setting water low state to OFF")

# https://www.home-assistant.io/integrations/mqtt/#discovery-messages
#  Note: homeassistant/<component>/[<node_id>/]<object_id>/config.
#  User device_class for auto suggestion on HA card picks
def send_discovery_messages(client):
    device_info = {
        "identifiers": [IDENTIFIER],
        "name": BASE_TOPIC,
        "manufacturer": "gardyn-of-eden",
        "model": MODEL,
        "sw_version": VERSION,
    }

    # Config for Light
    TEMP_CONFIG_TOPIC = "homeassistant/light/gardyn/"+IDENTIFIER+"_light/config"
    temp_config_payload = {
        "name": "Light",
        "unique_id": IDENTIFIER + "_light",
        "platform": "mqtt",
        "state_topic": BASE_TOPIC + "/light/state",
        "command_topic": BASE_TOPIC + "/light/command",
        "brightness_state_topic": BASE_TOPIC + "/light/brightness/state",
        "brightness_command_topic": BASE_TOPIC + "/light/brightness/set",
        "brightness_scale": 100,
        "device": device_info
    }
    safe_publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

    #Config for Pump (as a light with speed control, for example)
    # todo: maybe use fan instead....
    TEMP_CONFIG_TOPIC = "homeassistant/light/gardyn/"+IDENTIFIER+"_pump/config"
    temp_config_payload = {
        "name": "Pump",
        "unique_id": IDENTIFIER + "_pump",
        "platform": "mqtt",
	"device_class": "fan",
        "state_topic": BASE_TOPIC + "/pump/state",
        "command_topic": BASE_TOPIC + "/pump/command",

        "brightness_state_topic": BASE_TOPIC + "/pump/speed/state",
        "brightness_command_topic": BASE_TOPIC + "/pump/speed/set",
        "brightness_scale": 100,

        # if using fan....
	# "percentage_state_topic": BASE_TOPIC + "/pump/speed/state",
	# "percentage_command_topic": BASE_TOPIC + "/pump/speed/set",
	# "speed_range_min": 1,
	# "speed_range_max": 100,
        "icon": "mdi:water-pump",
        "device": device_info
    }
    safe_publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

    #Config for Temperature from PCB
    TEMP_CONFIG_TOPIC = "homeassistant/sensor/gardyn/"+IDENTIFIER+"_pcb_temp/config"
    temp_config_payload = {
        "name": "PCB Temperature",
        "unique_id": IDENTIFIER + "_pcb_temp",
        "state_topic": BASE_TOPIC + "/pcb/temperature",
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "device": device_info
    }
    safe_publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

    #Config for Temperature Sensor
    TEMP_CONFIG_TOPIC = "homeassistant/sensor/gardyn/"+IDENTIFIER+"_temperature/config"
    temp_config_payload = {
        "name": "Temperature",
        "unique_id": IDENTIFIER + "_temperature",
        "state_topic": BASE_TOPIC + "/temperature",
        "command_topic": BASE_TOPIC + "/temperature/get",
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "device": device_info
    }
    safe_publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

    #Config for Humidity Sensor
    TEMP_CONFIG_TOPIC = "homeassistant/sensor/gardyn/"+IDENTIFIER+"_humidity/config"
    temp_config_payload = {
        "name": "Humidity",
        "unique_id": IDENTIFIER + "_humidity",
        "state_topic": BASE_TOPIC + "/humidity",
        "command_topic": BASE_TOPIC + "/humidity/get",
        "unit_of_measurement": "%",
        "device_class": "humidity",
        "device": device_info
    }
    safe_publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)


    #Config for Water Level Sensor
    TEMP_CONFIG_TOPIC = "homeassistant/sensor/gardyn/"+IDENTIFIER+"_water_level/config"

    temp_config_payload = {
        "name": "Water Level",
        "unique_id": IDENTIFIER + "_water_level",
        "state_topic": BASE_TOPIC + "/water/level",
        "command_topic": BASE_TOPIC + "/water/level/get",
        "unit_of_measurement": "cm",
        "device_class": "distance",
        "device": device_info
    }
    safe_publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

    # Config for Water Low Binary Sensor
    TEMP_CONFIG_TOPIC = f"homeassistant/binary_sensor/gardyn/{IDENTIFIER}_water_low/config"
    temp_config_payload = {
        "name": "Water Low",
        "unique_id": IDENTIFIER + "_water_low",
        "platform": "mqtt",
        "state_topic": BASE_TOPIC + "/water/low/state",
        "device_class": "problem",
        "payload_on": "ON",
        "payload_off": "OFF",
        "device": device_info
    }
    safe_publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

    # Config for Water Low Threshold (current value)
        # Config for Water Low CM Set Number
    TEMP_CONFIG_TOPIC = f"homeassistant/number/gardyn/{IDENTIFIER}_water_low_cm/config"
    temp_config_payload = {
        "name": "Set Water Low Threshold",
        "unique_id": IDENTIFIER + "_water_low_cm",
        "platform": "mqtt",
        "state_topic": BASE_TOPIC + "/water/low/cm",
        "command_topic": BASE_TOPIC + "/water/low/cm/set",
        "min": 0,
        "max": 15,
        "step": 0.5,
        "unit_of_measurement": "cm",
        "device_class": "distance",
        "device": device_info
    }
    safe_publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

    # Config for Water Low Mode (Enabled/Disabled)
    TEMP_CONFIG_TOPIC = f"homeassistant/sensor/gardyn/{IDENTIFIER}_water_low_mode/config"
    temp_config_payload = {
        "name": "Water Low Mode",
        "unique_id": IDENTIFIER + "_water_low_mode",
        "platform": "mqtt",
        "state_topic": BASE_TOPIC + "/water/low/mode",
        "icon": "mdi:toggle-switch",  # Optional: or use mdi:alert for dramatic effect
        "device": device_info
    }
    safe_publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

    # Discovery configuration for Camera A (image entity)
    TEMP_CONFIG_TOPIC = "homeassistant/image/gardyn/" + IDENTIFIER + "_upper_camera/config"
    temp_config_payload = {
        "name": "Upper Camera",
        "unique_id": IDENTIFIER + "_upper_camera",
        "image_topic": BASE_TOPIC + "/image/upper_camera",
        "encoding": "b64",
        "content_type": "image/jpeg",
        "object_id": IDENTIFIER + "_upper_camera",
        "device": device_info
    }
    safe_publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

    # Discovery configuration for Camera B (image entity)
    TEMP_CONFIG_TOPIC = "homeassistant/image/gardyn/" + IDENTIFIER + "_lower_camera/config"
    temp_config_payload = {
        "name": "Lower Camera",
        "unique_id": IDENTIFIER + "_lower_camera",
        "image_topic": BASE_TOPIC + "/image/lower_camera",
        "encoding": "b64",
        "content_type": "image/jpeg",
        "object_id": IDENTIFIER + "_lower_camera",
        "device": device_info
    }
    safe_publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

def on_connect(client, userdata, flags, rc, properties=None):
    logger.info(f"Connected with result code {rc}")
    client.subscribe(BASE_TOPIC + "/#")
    # client.subscribe(BASE_TOPIC + "/light/brightness/set")
    send_discovery_messages(client)
    # Flush any persisted publishes queued while offline
    try:
        flush_queue(client)
    except Exception:
        logger.exception("Failed to flush publish queue on connect")
    publish_water_low_mode(client)

def on_message(client, userdata, msg):
    global brightness, speed, WATER_LOW_CM

    # Handle binary payloads (like image topics) — skip decoding
    if msg.topic.endswith("/image/upper_camera") or msg.topic.endswith("/image/lower_camera"):
        logger.debug(f"Received binary image on topic {msg.topic}, skipping decode.")
        return

    try:
        payload = msg.payload.decode("utf-8").strip()
        logger.debug(f"Decoded payload on {msg.topic}: '{payload}'")
    except UnicodeDecodeError:
        logger.error(f"Failed to decode message on topic {msg.topic}. Likely binary.")
        return

    topic_suffix = msg.topic.replace(BASE_TOPIC + "/", "")

    try:
        # === Pump Logic ===
        if topic_suffix == "pump/command":
            if payload.upper() == "ON":
                if WATER_LOW_CM not in (None, 0):
                    distance = safe_distance_measure()
                    if distance is not None and distance > WATER_LOW_CM:
                        logger.warning(f"Water too low ({distance:.2f}cm > {WATER_LOW_CM:.2f}cm), aborting pump")
                        flash_lights()
                        safe_publish(BASE_TOPIC + "/water/low/state", "ON", retain=True)
                        return
                    else:
                        safe_publish(BASE_TOPIC + "/water/low/state", "OFF", retain=True)
                pump.set_speed(speed)
                safe_publish(BASE_TOPIC + "/pump/state", "ON")
            elif payload.upper() == "OFF":
                pump.off()
                safe_publish(BASE_TOPIC + "/pump/state", "OFF")

        elif topic_suffix == "pump/speed/set" and payload.isdigit():
            speed = int(payload)
            pump.set_speed(speed)
            safe_publish(BASE_TOPIC + "/pump/speed/state", str(speed))

        # === Light Logic ===
        elif topic_suffix == "light/command":
            if payload.upper() == "ON":
                light.set_duty_cycle(brightness)
                safe_publish(BASE_TOPIC + "/light/state", "ON")
            elif payload.upper() == "OFF":
                light.off()
                safe_publish(BASE_TOPIC + "/light/state", "OFF")

        elif topic_suffix == "light/brightness/set" and payload.isdigit():
            brightness = int(payload)
            light.set_duty_cycle(brightness)
            safe_publish(BASE_TOPIC + "/light/brightness/state", str(brightness))

        # === Water Level ===
        elif topic_suffix == "water/level/get":
            distance = safe_distance_measure()
            if distance is not None:
                safe_publish(BASE_TOPIC + "/water/level", f"{distance:.2f}")

        elif topic_suffix == "water/low/cm/set":
            try:
                WATER_LOW_CM = float(payload)
                safe_publish(BASE_TOPIC + "/water/low/cm", f"{WATER_LOW_CM:.2f}", retain=True)
                publish_water_low_mode(client)
                update_water_low_state(client)
            except ValueError:
                logger.error(f"Invalid water low cm value: {payload}")

        # Handle retained/current threshold published by other clients or broker (load on connect)
        elif topic_suffix == "water/low/cm":
            try:
                WATER_LOW_CM = float(payload)
                logger.info(f"Loaded water low threshold from broker: {WATER_LOW_CM:.2f}cm")
                # Ensure mode/state reflect the newly loaded threshold
                publish_water_low_mode(client)
                update_water_low_state(client)
            except ValueError:
                logger.error(f"Invalid water low cm value from broker: {payload}")

        # === Sensor Data on Request ===
        elif topic_suffix == "pcb/temperature/get":
            pcb_temp = get_pcb_temperature()
            safe_publish(BASE_TOPIC + "/pcb/temperature", f"{pcb_temp:.2f}")

        elif topic_suffix == "temperature/get":
            temperature = temperature_sensor.read()
            safe_publish(BASE_TOPIC + "/temperature", f"{temperature:.2f}")

        elif topic_suffix == "humidity/get":
            humidity = humidity_sensor.read()
            safe_publish(BASE_TOPIC + "/humidity", f"{humidity:.2f}")

    except Exception as e:
        logger.exception(f"Error handling message on topic {msg.topic}: {e}")

def publish_pcb_temperature(client):
    while not stop_event.is_set():
        try:
            pcb_temp = get_pcb_temperature()
            logger.info(f"Publishing PCB Temperature: {pcb_temp:.2f}°C")
            safe_publish(BASE_TOPIC + "/pcb/temperature", f"{pcb_temp:.2f}")
        except Exception as e:
            logger.error(f"Failed to read or publish PCB temperature: {e}")
        if stop_event.wait(publish_frequency):
            break

def publish_temperature(client):
    while not stop_event.is_set():
        try:
            temperature = temperature_sensor.read()
            logger.info(f"Publishing Temperature: {temperature:.2f}°C")
            safe_publish(BASE_TOPIC + "/temperature", f"{temperature:.2f}")
        except Exception as e:
            logger.error(f"Failed to read or publish ambient temperature: {e}")
        if stop_event.wait(publish_frequency):
            break

def publish_humidity(client):
    while not stop_event.is_set():
        try:
            humidity = humidity_sensor.read()
            logger.info(f"Publishing Humidity: {humidity:.2f}%")
            safe_publish(BASE_TOPIC + "/humidity", f"{humidity:.2f}")
        except Exception as e:
            logger.error(f"Failed to read or publish ambient humidity: {e}")
        if stop_event.wait(publish_frequency):
            break

def publish_water_level(client):
    while not stop_event.is_set():
        distance = safe_distance_measure()
        if distance is not None:
            logger.info(f"Publishing Water Level: {distance:.2f}cm")
            safe_publish(BASE_TOPIC + "/water/level", f"{distance:.2f}")
        if stop_event.wait(publish_frequency):
            break

def publish_images(client):
    while not stop_event.is_set():
        try:
            # Capture upper camera image
            subprocess.check_call([
                'fswebcam', '-d', UPPER_CAMERA_DEVICE, '-r', CAMERA_RESOLUTION,
                '-S', '2', '-F', '2', '--no-banner', UPPER_IMAGE_PATH
            ])
            logger.info(f"Captured image from upper camera ({UPPER_CAMERA_DEVICE})")

            # Capture lower camera image
            subprocess.check_call([
                'fswebcam', '-d', LOWER_CAMERA_DEVICE, '-r', CAMERA_RESOLUTION,
                '-S', '2', '-F', '2', '--no-banner', LOWER_IMAGE_PATH
            ])
            logger.info(f"Captured image from lower camera ({LOWER_CAMERA_DEVICE})")

            # Publish upper camera image
            with open(UPPER_IMAGE_PATH, 'rb') as f:
                upper_cam_jpeg_data = f.read()  # Read as raw binary
                safe_publish(BASE_TOPIC + "/image/upper_camera", payload=upper_cam_jpeg_data, qos=0, retain=False)
                logger.info("Published image to /image/upper_camera")

            # Publish lower camera image
            with open(LOWER_IMAGE_PATH, 'rb') as f:
                lower_cam_jpeg_data = f.read()  # Read as raw binary
                safe_publish(BASE_TOPIC + "/image/lower_camera", payload=lower_cam_jpeg_data, qos=0, retain=False)
                logger.info("Published image to /image/lower_camera")

        except subprocess.CalledProcessError as e:
            logger.error(f"Camera capture failed: {e}")
        except Exception as e:
            logger.exception("Unexpected error during image capture/publish")

        if stop_event.wait(IMAGE_INTERVAL_SECONDS):
            break

def publish_water_low_state_periodic(client):
    """Periodically call `update_water_low_state` using the configured publish_frequency."""
    while not stop_event.is_set():
        try:
            update_water_low_state(client)
        except Exception:
            logger.exception("Error while periodically publishing water low state")
        if stop_event.wait(publish_frequency):
            break


if __name__ == "__main__":
    logger.info(f"Connecting to {BROKER} on port {PORT} with keep alive {KEEP_ALIVE_INTERVAL}")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(USERNAME, PASSWORD)
    client.connect(BROKER, PORT, KEEP_ALIVE_INTERVAL)

    # start mqtt network loop in background so we can manage threads and shutdown
    client.loop_start()

    threads = []

    pcb_temp_thread = threading.Thread(target=publish_pcb_temperature, args=(client,))
    pcb_temp_thread.daemon = False
    pcb_temp_thread.start()
    threads.append(pcb_temp_thread)

    temperature_thread = threading.Thread(target=publish_temperature, args=(client,))
    temperature_thread.daemon = False
    temperature_thread.start()
    threads.append(temperature_thread)

    humidity_thread = threading.Thread(target=publish_humidity, args=(client,))
    humidity_thread.daemon = False
    humidity_thread.start()
    threads.append(humidity_thread)

    water_level_thread = threading.Thread(target=publish_water_level, args=(client,))
    water_level_thread.daemon = False
    water_level_thread.start()
    threads.append(water_level_thread)

    water_low_state_thread = threading.Thread(target=publish_water_low_state_periodic, args=(client,))
    water_low_state_thread.daemon = False
    water_low_state_thread.start()
    threads.append(water_low_state_thread)

    publish_images_thread = threading.Thread(target=publish_images, args=(client,))
    publish_images_thread.daemon = False
    publish_images_thread.start()
    threads.append(publish_images_thread)

    # handle signals to gracefully shutdown
    def _handle_signal(signum, frame):
        logger.info(f"Signal {signum} received, initiating shutdown")
        stop_event.set()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    try:
        # wait until stop_event is set by signal handler
        stop_event.wait()
    finally:
        logger.info("Shutting down: stopping mqtt loop and joining threads")
        try:
            client.loop_stop()
            client.disconnect()
        except Exception:
            logger.exception("Error stopping MQTT client")
        for t in threads:
            t.join(timeout=5)
        logger.info("Shutdown complete")
