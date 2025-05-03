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
from app.sensors.temperature.temperature import temperature_sensor
from app.sensors.humidity.humidity import humidity_sensor
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

logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")

# Initialize devices
pin_factory = PiGPIOFactory()

pump = Pump(pin_factory=pin_factory)
light = Light(pin_factory=pin_factory)
distance_sensor = Distance(pin_factory=pin_factory)

# default on brightness
brightness  = 50
speed       = 100
sec_per_min = 60
min_per_hr  = 60

# publish twice an hour
publish_frequency = sec_per_min * min_per_hr / 2

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
        client.publish(BASE_TOPIC + "/light/state", "ON")
    else:
        logger.info("Toggling Light OFF")
        light.off()
        client.publish(BASE_TOPIC + "/light/state", "OFF")

def toggle_pump():
    global pump_state
    pump_state = not pump_state
    if pump_state:
        logger.info("Toggling Pump ON")
        pump.set_speed(speed)
        client.publish(BASE_TOPIC + "/pump/state", "ON")
    else:
        logger.info("Toggling Pump OFF")
        pump.off()
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
    global brightness
    global speed
    global WATER_LOW_CM

    logger.debug(f"Message received on topic {msg.topic}: {msg.payload}")
    try:
        payload = msg.payload.decode("utf-8")
        logger.debug(f"Decoded payload: '{payload}'")
        topic = msg.topic.split("/")[-1]

        # Handle pump commands
        if msg.topic == BASE_TOPIC + "/pump/command":
            if payload.upper() == "ON":
                if WATER_LOW_CM not in (None, 0):
                    distance = safe_distance_measure()
                    if distance is not None:
                        if distance > WATER_LOW_CM:
                            logger.warning(f"Water level too low ({distance:.2f}cm > {WATER_LOW_CM:.2f}cm), flashing lights, not running pump")
                            flash_lights()
                            client.publish(BASE_TOPIC + "/water/low/state", "ON", retain=True)
                            return  # Don't run the pump
                        else:
                            logger.info(f"Water level OK ({distance:.2f}cm <= {WATER_LOW_CM:.2f}cm), running pump")
                            client.publish(BASE_TOPIC + "/water/low/state", "OFF", retain=True)
                    else:
                        logger.error("Failed to read water level, running pump anyway")
                else:
                    logger.info("Water low checking disabled (None or 0 threshold), running pump without checking")

                pump.set_speed(speed)
                client.publish(BASE_TOPIC + "/pump/state", "ON")

            elif payload.upper() == "OFF":
                logger.info("/pump/state OFF")
                pump.off()
                client.publish(BASE_TOPIC + "/pump/state", "OFF")

        elif msg.topic == BASE_TOPIC + "/pump/speed/set":
            if payload.isdigit():  # Ensure payload is a digit
                speed = int(payload)
                pump.set_speed(speed)
                logger.info(f"/pump/speed/state {speed}")
                client.publish(BASE_TOPIC + "/pump/speed/state", str(speed))
            else:
                logger.error("Invalid speed value received.")

        # Handle light commands
        if msg.topic == BASE_TOPIC + "/light/command":
            if payload.upper() == "ON":
                light.set_duty_cycle(brightness)
                logger.info("/light/state ON")
                client.publish(BASE_TOPIC + "/light/state", "ON")
            elif payload.upper() == "OFF":
                light.off()
                logger.info("/light/state OFF")
                client.publish(BASE_TOPIC + "/light/state", "OFF")
        elif msg.topic == BASE_TOPIC + "/light/brightness/set":
            if payload.isdigit():  # Ensure payload is a digit
                brightness = int(payload)
                light.set_duty_cycle(brightness)
                logger.info(f"/light/brightness/state {brightness}")
                client.publish(BASE_TOPIC + "/light/brightness/state", str(brightness))
            else:
                logger.error("Invalid brightness value received.")

        # on demand sensor readings
        if msg.topic == BASE_TOPIC + "/water/level/get":
            try:
                distance = distance_sensor.measure_once()
                if distance is None:
                    logger.warning("No echo received; sensor might be out of range.")
                else:
                    logger.info(f"Received on-demand water level request: {distance:.2f}cm")
                    client.publish(BASE_TOPIC + "/water/level", f"{distance:.2f}")
            except Exception as e:
                logger.error(f"Failed to fetch and publish on-demand water level: {e}")

        if msg.topic == BASE_TOPIC + "/water/low/cm/set":
            try:
                WATER_LOW_CM = float(payload)
                logger.info(f"Updated WATER_LOW_CM threshold to {WATER_LOW_CM}cm")
                client.publish(BASE_TOPIC + "/water/low/cm", f"{WATER_LOW_CM:.2f}", retain=True)
                publish_water_low_mode(client)
                update_water_low_state(client)
            except ValueError:
                logger.error(f"Invalid water low cm set value received: {payload}")


        if msg.topic == BASE_TOPIC + "/pcb/temperature/get":
            try:
                pcb_temp = get_pcb_temperature()
                logger.info(f"Publishing PCB Temperature: {pcb_temp:.2f}°C")
                client.publish(BASE_TOPIC + "/pcb/temperature", f"{pcb_temp:.2f}")
            except Exception as e:
                logger.error(f"Failed to read or publish pcb temperature: {e}")

        if msg.topic == BASE_TOPIC + "/temperature/get":
            try:
                temperature = temperature_sensor.read()
                logger.info(f"Publishing PCB Temperature: {temperature:.2f}°C")
                client.publish(BASE_TOPIC + "/temperature", f"{temperature:.2f}")
            except Exception as e:
                logger.error(f"Failed to read or publish ambient temperature: {e}")

        if msg.topic == BASE_TOPIC + "/humidity/get":
            try:
                humidity = humidity_sensor.read()
                logger.info(f"Publishing Humidity: {humidity:.2f}%")
                client.publish(BASE_TOPIC + "/humidity", f"{humidity:.2f}")
            except Exception as e:
                logger.error(f"Failed to read or publish ambient humidity: {e}")

    except UnicodeDecodeError as e:
        logger.error(f"Error decoding message: {e}. Data may not be text.")
    except ValueError as e:
        logger.error(f"ValueError encountered: {e}")

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
            temperature = temperature_sensor.read()
            logger.info(f"Publishing Temperature: {temperature:.2f}°C")
            client.publish(BASE_TOPIC + "/temperature", f"{temperature:.2f}")
        except Exception as e:
            logger.error(f"Failed to read or publish ambient temperature: {e}")
        sleep(30*60)  # Publish frequency, every x seconds

def publish_humidity(client):
    while True:
        try:
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

def publish_images(client):
    while True:
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
                client.publish(BASE_TOPIC + "/image/upper_camera", payload=upper_cam_jpeg_data, qos=0, retain=False)
                logger.info("Published image to /image/upper_camera")

            # Publish lower camera image
            with open(LOWER_IMAGE_PATH, 'rb') as f:
                lower_cam_jpeg_data = f.read()  # Read as raw binary
                client.publish(BASE_TOPIC + "/image/lower_camera", payload=lower_cam_jpeg_data, qos=0, retain=False)
                logger.info("Published image to /image/lower_camera")

        except subprocess.CalledProcessError as e:
            logger.error(f"Camera capture failed: {e}")
        except Exception as e:
            logger.exception("Unexpected error during image capture/publish")

        sleep(IMAGE_INTERVAL_SECONDS)


if __name__ == "__main__":
    logger.info(f"Connecting to {BROKER} on port {PORT} with keep alive {KEEP_ALIVE_INTERVAL}")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(USERNAME, PASSWORD)
    client.connect(BROKER, PORT, KEEP_ALIVE_INTERVAL)

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
