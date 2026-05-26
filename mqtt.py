import subprocess
import threading
from threading import Timer
import logging
import paho.mqtt.client as mqtt
import base64
import json
# import picamera
# import cv2
from time import sleep
from config import USERNAME, PASSWORD, BROKER, PORT, KEEP_ALIVE_INTERVAL, BASE_TOPIC, IDENTIFIER, MODEL, VERSION, WATER_LOW_CM, UPPER_CAMERA_DEVICE, LOWER_CAMERA_DEVICE, UPPER_IMAGE_PATH, LOWER_IMAGE_PATH, CAMERA_RESOLUTION, IMAGE_INTERVAL_SECONDS

from gpiozero import Button  # Import gpiozero Button
from gpiozero.pins.pigpio import PiGPIOFactory

from app.sensors.light.light import Light
from app.sensors.pump.pump import Pump
from app.sensors.pcb_temp.pcb_temp import get_pcb_temperature
from app.sensors.temperature.temperature import get_temperature_sensor
from app.sensors.humidity.humidity import get_humidity_sensor
from app.sensors.distance.distance import Distance, MeasurementError

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("gardyn.log"),  # Log to a file
        logging.StreamHandler()  # Log to the console (stdout)
    ]
)

logger = logging.getLogger(__name__)

# set to INFO, for to capture mqtt messages at info-level messages.
logger.setLevel(logging.WARNING)

pin_factory = None
pump = None
light = None
distance_sensor = None
button = None
client = None
capture_lock = threading.Lock()
distance_measure_lock = threading.Lock()

# default on brightness
brightness  = 50
speed       = 100
DEFAULT_BRIGHTNESS = 50
DEFAULT_SPEED = 100
sec_per_min = 60
min_per_hr  = 60

# publish twice an hour
publish_frequency = sec_per_min * min_per_hr / 2

# Variables to track the state of the light and pump
light_state = False
pump_state = False
double_press_time = 1  # Time to detect a double press (in seconds)
press_count = 0
double_press_timer = None

def get_pin_factory():
    global pin_factory
    if pin_factory is None:
        pin_factory = PiGPIOFactory()
    return pin_factory

def get_pump():
    global pump
    if pump is None:
        pump = Pump(pin_factory=get_pin_factory())
    return pump

def get_light():
    global light
    if light is None:
        light = Light(pin_factory=get_pin_factory())
    return light

def get_distance_sensor():
    global distance_sensor
    if distance_sensor is None:
        distance_sensor = Distance(pin_factory=get_pin_factory())
    return distance_sensor

def configure_button_handlers():
    global button
    if button is None:
        button_pin = 13
        button = Button(button_pin, pin_factory=get_pin_factory(), bounce_time=0.2, hold_time=2)
        button.when_pressed = handle_button_press

def initialize_devices():
    get_pump()
    get_light()
    get_distance_sensor()
    configure_button_handlers()

# Button press callbacks
def toggle_light():
    global light_state
    light_state = not light_state
    if light_state:
        logger.info("Toggling Light ON")
        get_light().set_duty_cycle(brightness)
        if client is not None:
            client.publish(BASE_TOPIC + "/light/state", "ON")
    else:
        logger.info("Toggling Light OFF")
        get_light().off()
        if client is not None:
            client.publish(BASE_TOPIC + "/light/state", "OFF")

def toggle_pump():
    global pump_state
    pump_state = not pump_state
    if pump_state:
        logger.info("Toggling Pump ON")
        get_pump().set_speed(speed)
        if client is not None:
            client.publish(BASE_TOPIC + "/pump/state", "ON")
    else:
        logger.info("Toggling Pump OFF")
        get_pump().off()
        if client is not None:
            client.publish(BASE_TOPIC + "/pump/state", "OFF")

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

# helpers
def flash_lights(times=3, delay=0.3):
    light_device = get_light()
    original_brightness = light_device.get_brightness()  # Save the brightness (0–100 scale)
    was_on = original_brightness > 0  # If >0%, we consider it "on"

    logger.info(f"Flashing lights {times} times. Original brightness: {original_brightness}%")

    for _ in range(times):
        light_device.off()
        sleep(delay)
        light_device.set_brightness(100)  # Flash full brightness for maximum visibility
        sleep(delay)
    # Restore original state
    if was_on:
        light_device.set_brightness(original_brightness)
    else:
        light_device.off()

def safe_distance_measure():
    global distance_sensor
    if not distance_measure_lock.acquire(blocking=False):
        logger.warning("Distance measure already in progress, skipping request")
        return None
    try:
        return get_distance_sensor().measure_once()
    except MeasurementError as e:
        logger.warning(f"Distance measure failed: {e}, trying recovery")
        try:
            if distance_sensor is not None:
                distance_sensor.cleanup()
            distance_sensor = Distance(pin_factory=get_pin_factory())
            return distance_sensor.measure_once()
        except Exception as e2:
            logger.error(f"Distance full recovery failed: {e2}")
            return None
    finally:
        distance_measure_lock.release()

def parse_percentage(payload, label):
    try:
        value = int(payload)
    except (TypeError, ValueError):
        logger.error(f"Invalid {label} value: {payload}")
        return None
    if not 0 <= value <= 100:
        logger.error(f"{label} must be between 0 and 100: {value}")
        return None
    return value

def publish_water_low_mode(client):
    if WATER_LOW_CM not in (None, 0):
        mode = "Enabled"
    else:
        mode = "Disabled"
    logger.info(f"Publishing water low mode: {mode}")
    client.publish(BASE_TOPIC + "/water/low/mode", mode, retain=True)


def update_water_low_state(client):
    if WATER_LOW_CM not in (None, 0):
        distance = safe_distance_measure()
        if distance is not None:
            if distance > WATER_LOW_CM:
                client.publish(BASE_TOPIC + "/water/low/state", "ON", retain=True)
                logger.info(f"Updated water low state to ON (distance {distance:.2f}cm > {WATER_LOW_CM:.2f}cm)")
            else:
                client.publish(BASE_TOPIC + "/water/low/state", "OFF", retain=True)
                logger.info(f"Updated water low state to OFF (distance {distance:.2f}cm <= {WATER_LOW_CM:.2f}cm)")
        else:
            logger.warning("Could not update water low state because distance reading failed")
    else:
        # If checking is disabled, maybe set it to OFF by default
        client.publish(BASE_TOPIC + "/water/low/state", "OFF", retain=True)
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
    client.publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

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
    client.publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

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
    client.publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

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
    client.publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

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
    client.publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)


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
    client.publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

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
    client.publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

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
    client.publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

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
    client.publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

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
    client.publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

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
    client.publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

def on_connect(client, userdata, flags, rc, properties=None):
    logger.info(f"Connected with result code {rc}")
    client.subscribe(BASE_TOPIC + "/#")
    # client.subscribe(BASE_TOPIC + "/light/brightness/set")
    send_discovery_messages(client)
    publish_water_low_mode(client)

def on_message(client, userdata, msg):
    global brightness, speed, WATER_LOW_CM, light_state, pump_state

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
                        client.publish(BASE_TOPIC + "/water/low/state", "ON", retain=True)
                        return
                    else:
                        client.publish(BASE_TOPIC + "/water/low/state", "OFF", retain=True)
                if speed <= 0:
                    speed = DEFAULT_SPEED
                get_pump().set_speed(speed)
                pump_state = True
                client.publish(BASE_TOPIC + "/pump/state", "ON")
                client.publish(BASE_TOPIC + "/pump/speed/state", str(speed))
            elif payload.upper() == "OFF":
                get_pump().off()
                pump_state = False
                client.publish(BASE_TOPIC + "/pump/state", "OFF")

        elif topic_suffix == "pump/speed/set":
            parsed_speed = parse_percentage(payload, "pump speed")
            if parsed_speed is None:
                return
            speed = parsed_speed
            if speed == 0:
                get_pump().off()
                pump_state = False
                client.publish(BASE_TOPIC + "/pump/state", "OFF")
            else:
                get_pump().set_speed(speed)
                pump_state = True
                client.publish(BASE_TOPIC + "/pump/state", "ON")
            client.publish(BASE_TOPIC + "/pump/speed/state", str(speed))

        # === Light Logic ===
        elif topic_suffix == "light/command":
            if payload.upper() == "ON":
                if brightness <= 0:
                    brightness = DEFAULT_BRIGHTNESS
                get_light().set_duty_cycle(brightness)
                light_state = True
                client.publish(BASE_TOPIC + "/light/state", "ON")
                client.publish(BASE_TOPIC + "/light/brightness/state", str(brightness))
            elif payload.upper() == "OFF":
                get_light().off()
                light_state = False
                client.publish(BASE_TOPIC + "/light/state", "OFF")

        elif topic_suffix == "light/brightness/set":
            parsed_brightness = parse_percentage(payload, "light brightness")
            if parsed_brightness is None:
                return
            brightness = parsed_brightness
            if brightness == 0:
                get_light().off()
                light_state = False
                client.publish(BASE_TOPIC + "/light/state", "OFF")
            else:
                get_light().set_duty_cycle(brightness)
                light_state = True
                client.publish(BASE_TOPIC + "/light/state", "ON")
            client.publish(BASE_TOPIC + "/light/brightness/state", str(brightness))

        # === Water Level ===
        elif topic_suffix == "water/level/get":
            distance = safe_distance_measure()
            if distance is not None:
                client.publish(BASE_TOPIC + "/water/level", f"{distance:.2f}")

        elif topic_suffix == "water/low/cm/set":
            try:
                WATER_LOW_CM = float(payload)
                client.publish(BASE_TOPIC + "/water/low/cm", f"{WATER_LOW_CM:.2f}", retain=True)
                publish_water_low_mode(client)
                update_water_low_state(client)
            except ValueError:
                logger.error(f"Invalid water low cm value: {payload}")

        # === Sensor Data on Request ===
        elif topic_suffix == "pcb/temperature/get":
            pcb_temp = get_pcb_temperature()
            client.publish(BASE_TOPIC + "/pcb/temperature", f"{pcb_temp:.2f}")

        elif topic_suffix == "temperature/get":
            temperature_sensor = get_temperature_sensor()
            if temperature_sensor is None:
                raise RuntimeError("Temperature sensor is not initialized")
            temperature = temperature_sensor.read()
            client.publish(BASE_TOPIC + "/temperature", f"{temperature:.2f}")

        elif topic_suffix == "humidity/get":
            humidity_sensor = get_humidity_sensor()
            if humidity_sensor is None:
                raise RuntimeError("Humidity sensor is not initialized")
            humidity = humidity_sensor.read()
            client.publish(BASE_TOPIC + "/humidity", f"{humidity:.2f}")

    except Exception as e:
        logger.exception(f"Error handling message on topic {msg.topic}: {e}")

def publish_pcb_temperature(client):
    while True:
        try:
            pcb_temp = get_pcb_temperature()
            logger.info(f"Publishing PCB Temperature: {pcb_temp:.2f}°C")
            client.publish(BASE_TOPIC + "/pcb/temperature", f"{pcb_temp:.2f}")
        except Exception as e:
            logger.error(f"Failed to read or publish PCB temperature: {e}")
        sleep(30*60)  # Publish frequency, every x seconds

def publish_temperature(client):
    while True:
        try:
            temperature_sensor = get_temperature_sensor()
            if temperature_sensor is None:
                raise RuntimeError("Temperature sensor is not initialized")
            temperature = temperature_sensor.read()
            logger.info(f"Publishing Temperature: {temperature:.2f}°C")
            client.publish(BASE_TOPIC + "/temperature", f"{temperature:.2f}")
        except Exception as e:
            logger.error(f"Failed to read or publish ambient temperature: {e}")
        sleep(30*60)  # Publish frequency, every x seconds

def publish_humidity(client):
    while True:
        try:
            humidity_sensor = get_humidity_sensor()
            if humidity_sensor is None:
                raise RuntimeError("Humidity sensor is not initialized")
            humidity = humidity_sensor.read()
            logger.info(f"Publishing Humidity: {humidity:.2f}%")
            client.publish(BASE_TOPIC + "/humidity", f"{humidity:.2f}")
        except Exception as e:
            logger.error(f"Failed to read or publish ambient humidity: {e}")
        sleep(30*60)  # Publish frequency, every x seconds

def publish_water_level(client):
    while True:
        distance = safe_distance_measure()
        if distance is not None:
            logger.info(f"Publishing Water Level: {distance:.2f}cm")
            client.publish(BASE_TOPIC + "/water/level", f"{distance:.2f}")
        sleep(30 * 60)

def capture_images(client):
    if not capture_lock.acquire(blocking=False):
        logger.warning("Camera capture already in progress, skipping request")
        return
    try:
        subprocess.check_call([
            'fswebcam', '-d', UPPER_CAMERA_DEVICE, '-r', CAMERA_RESOLUTION,
            '-S', '2', '-F', '2', '--no-banner', UPPER_IMAGE_PATH
        ])
        logger.info(f"Captured image from upper camera ({UPPER_CAMERA_DEVICE})")

        subprocess.check_call([
            'fswebcam', '-d', LOWER_CAMERA_DEVICE, '-r', CAMERA_RESOLUTION,
            '-S', '2', '-F', '2', '--no-banner', LOWER_IMAGE_PATH
        ])
        logger.info(f"Captured image from lower camera ({LOWER_CAMERA_DEVICE})")

        with open(UPPER_IMAGE_PATH, 'rb') as f:
            upper_cam_jpeg_data = f.read()
            client.publish(BASE_TOPIC + "/image/upper_camera", payload=upper_cam_jpeg_data, qos=0, retain=False)
            logger.info("Published image to /image/upper_camera")

        with open(LOWER_IMAGE_PATH, 'rb') as f:
            lower_cam_jpeg_data = f.read()
            client.publish(BASE_TOPIC + "/image/lower_camera", payload=lower_cam_jpeg_data, qos=0, retain=False)
            logger.info("Published image to /image/lower_camera")
    finally:
        capture_lock.release()

def publish_images(client):
    while True:
        try:
            capture_images(client)

        except subprocess.CalledProcessError as e:
            logger.error(f"Camera capture failed: {e}")
        except Exception as e:
            logger.exception("Unexpected error during image capture/publish")

        sleep(IMAGE_INTERVAL_SECONDS)


if __name__ == "__main__":
    logger.info(f"Connecting to {BROKER} on port {PORT} with keep alive {KEEP_ALIVE_INTERVAL}")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"{IDENTIFIER}_mqtt")
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(USERNAME, PASSWORD)
    client.connect(BROKER, PORT, KEEP_ALIVE_INTERVAL)
    initialize_devices()

    pcb_temp_thread = threading.Thread(target=publish_pcb_temperature, args=(client,))
    pcb_temp_thread.daemon = True
    pcb_temp_thread.start()

    temperature_thread = threading.Thread(target=publish_temperature, args=(client,))
    temperature_thread.daemon = True
    temperature_thread.start()

    humidity_thread = threading.Thread(target=publish_humidity, args=(client,))
    humidity_thread.daemon = True
    humidity_thread.start()

    water_level_thread = threading.Thread(target=publish_water_level, args=(client,))
    water_level_thread.daemon = True
    water_level_thread.start()


    publish_images_thread = threading.Thread(target=publish_images, args=(client,))
    publish_images_thread.daemon = True
    publish_images_thread.start()

    client.loop_forever()
