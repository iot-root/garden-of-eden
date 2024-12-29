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
from config import USERNAME, PASSWORD, BROKER, PORT, KEEP_ALIVE_INTERVAL, BASE_TOPIC, IDENTIFIER, MODEL, VERSION

from gpiozero import Button  # Import gpiozero Button
from gpiozero.pins.pigpio import PiGPIOFactory

from app.sensors.light.light import Light
from app.sensors.pump.pump import Pump
from app.sensors.pcb_temp.pcb_temp import get_pcb_temperature
from app.sensors.temperature.temperature import temperature_sensor
from app.sensors.humidity.humidity import humidity_sensor
from app.sensors.distance.distance import Distance

# Configure logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("gardyn.log"),  # Log to a file
        logging.StreamHandler()  # Log to the console (stdout)
    ]
)

logger = logging.getLogger(__name__)

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

# camera = picamera.PiCamera()
# camera.vflip=True

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

def send_discovery_messages(client):
    device_info = {
        "identifiers": [IDENTIFIER],
        "name": BASE_TOPIC,
        "manufacturer": "gardyn-of-eden",
        "model": MODEL,
        "sw_version": VERSION,
    }

    #Note: homeassistant/<component>/[<node_id>/]<object_id>/config.

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

    #Config for Pump (as a switch with speed control, for example)
    TEMP_CONFIG_TOPIC = "homeassistant/light/gardyn/"+IDENTIFIER+"_pump/config"
    temp_config_payload = {
        "name": "Pump",
        "unique_id": IDENTIFIER + "_pump",
        "platform": "mqtt",
        "state_topic": BASE_TOPIC + "/pump/state",
        "command_topic": BASE_TOPIC + "/pump/command",
        "percentage_state_topic": BASE_TOPIC + "/pump/speed/state",
        "percentage_command_topic": BASE_TOPIC + "/pump/speed/set",
        "speed_range_max": 100,
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

    TEMP_CONFIG_TOPIC = "homeassistant/camera/gardyn/"+IDENTIFIER+"_cameraleft/config"
    temp_config_payload = {
        "name": "Left Camera",
        "unique_id": IDENTIFIER + "cameraleft",
        "state_topic": BASE_TOPIC + "/camera/left",
        "device": device_info
    }
    client.publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)

    TEMP_CONFIG_TOPIC = "homeassistant/camera/gardyn/"+IDENTIFIER+"_cameraright/config"
    temp_config_payload = {
        "name": "Right Camera",
        "unique_id": IDENTIFIER + "cameraright",
        "state_topic": BASE_TOPIC + "/camera/right",
        "device": device_info
    }
    client.publish(TEMP_CONFIG_TOPIC, json.dumps(temp_config_payload), retain=True)


def on_connect(client, userdata, flags, rc, properties=None):
    logger.info(f"Connected with result code {rc}")
    client.subscribe(BASE_TOPIC + "/#")
    # client.subscribe(BASE_TOPIC + "/light/brightness/set")
    send_discovery_messages(client)

def on_message(client, userdata, msg):
    logger.debug(f"Message received on topic {msg.topic}: {msg.payload}")
    try:
        payload = msg.payload.decode("utf-8")
        logger.debug(f"Decoded payload: '{payload}'")
        topic = msg.topic.split("/")[-1]

        global brightness
        global speed

        # Handle pump commands
        if msg.topic == BASE_TOPIC + "/pump/command":
            if payload.upper() == "ON":
                logger.info("/pump/state ON")
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
        sleep(30*60)  # Publish temperature every x seconds

def publish_temperature(client):
    while True:
        try:
            temperature = temperature_sensor.read()
            logger.info(f"Publishing Temperature: {temperature:.2f}°C")
            client.publish(BASE_TOPIC + "/temperature", f"{temperature:.2f}")
        except Exception as e:
            logger.error(f"Failed to read or publish ambient temperature: {e}")
        sleep(30*60)  # Publish temperature every x seconds

def publish_humidity(client):
    while True:
        try:
            humidity = humidity_sensor.read()
            logger.info(f"Publishing Humidity: {humidity:.2f}%")
            client.publish(BASE_TOPIC + "/humidity", f"{humidity:.2f}")
        except Exception as e:
            logger.error(f"Failed to read or publish ambient humidity: {e}")
        sleep(30*60)  # Publish temperature every x seconds

def publish_water_level(client):
    while True:
        try:
            distance = distance_sensor.measure_once()
            logger.info(f"Publishing Water Level: {distance:.2f}cm")
            client.publish(BASE_TOPIC + "/water/level", f"{distance:.2f}")
        except Exception as e:
            logger.error(f"Failed to read or publish water level: {e}")
        sleep(30*60)  # Publish temperature every x seconds

# def publish_images(client):
    # while True:
        # try:
            # cap = cv2.VideoCapture('/dev/video0')
            # ret, frame = cap.read()
            # cap.release()
            # if not ret:
                # raise ValueError("Could not read from device")
            # image = cv2.imencode('.jpg', frame)[1].tobytes()
            # client.publish(BASE_TOPIC+"/camera/right",payload=image)

            # cap = cv2.VideoCapture('/dev/video1')
            # ret, frame = cap.read()
            # cap.release()
            # if not ret:
                # raise ValueError("Could not read from device")
            # image = cv2.imencode('.jpg', frame)[1].tobytes()
            # client.publish(BASE_TOPIC+"/camera/left",payload=image)
        # except Exception as e:
            # logger.error(f"Failed to read or publish water level: {e}")
    # sleep(60*60*24)  # Publish temperature every 60 seconds

# def publish_images(client):
    # while True:
        # try:
            # # Define paths for the left and right camera images
            # left_image_path = '/tmp/camera_left.jpg'
            # right_image_path = '/tmp/camera_right.jpg'

            # # Capture images from the cameras
            # subprocess.run(['fswebcam', '-r', '640x480', '--no-banner', left_image_path], check=True)
            # subprocess.run(['fswebcam', '-r', '640x480', '--no-banner', right_image_path], check=True)

            # # Read and publish the left image
            # with open(left_image_path, 'rb') as image_file:
                # left_image = image_file.read()
            # client.publish(BASE_TOPIC+"/camera/left", payload=left_image)

            # # Read and publish the right image
            # with open(right_image_path, 'rb') as image_file:
                # right_image = image_file.read()
            # client.publish(BASE_TOPIC+"/camera/right", payload=right_image)

        # except subprocess.CalledProcessError as e:
            # logger.error(f"Failed to capture images: {e}")
        # except Exception as e:
            # logger.error(f"Failed to read or publish images: {e}")

        # sleep(60*60*24)  # Adjust the sleep duration as needed

def capture_and_publish_image(client, camera_position):
    # Initialize the camera
    camera = PiCamera()
    camera.resolution = (640, 480)
    sleep(2)  # Camera warm-up time

    file_name = camera_position + '_image_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.jpg'
    print(f'Taking photo for {camera_position}')

    # Capture image into an in-memory stream
    image_stream = BytesIO()
    camera.capture(image_stream, 'jpeg')
    image_stream.seek(0)  # Rewind the stream to the beginning so we can read its content
    image_data = image_stream.read()

    # Optional: Save the image file locally
    with open(file_name, "wb") as imageFile:
        imageFile.write(image_data)

    # Publish the image
    encoded_image = base64.b64encode(image_data).decode('utf-8')
    client.publish(BASE_TOPIC + f"/camera/{camera_position}", payload=encoded_image)
    print(f'{file_name} image published')

def publish_images(client):
    while True:
        try:
            # Capture and publish images for the left and right positions
            capture_and_publish_image(client,'left')
            capture_and_publish_image(client,'right')

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            # Handle other unexpected errors

        # Adjust the sleep duration as needed, e.g., for a 1-hour interval, use sleep(3600)
        sleep(30)  # Sleep for 1 hour before the next capture cycle

# def publish_images(client):
    # while True:
        # try:
            # # Define paths for the left and right camera images
            # left_image_path = '/tmp/camera_left.jpg'
            # right_image_path = '/tmp/camera_right.jpg'

            # # Capture images from the cameras
            # subprocess.check_call(['fswebcam', '-r', '640x480', '--no-banner', left_image_path])
            # subprocess.check_call(['fswebcam', '-r', '640x480', '--no-banner', right_image_path])

            # # Read, encode in Base64, and publish the left image
            # with open(left_image_path, 'rb') as image_file:
                # left_image = base64.b64encode(image_file.read()).decode('utf-8')
            # client.publish(BASE_TOPIC + "/camera/left", payload=left_image)

            # # Read, encode in Base64, and publish the right image
            # with open(right_image_path, 'rb') as image_file:
                # right_image = base64.b64encode(image_file.read()).decode('utf-8')
            # client.publish(BASE_TOPIC + "/camera/right", payload=right_image)

        # except subprocess.CalledProcessError as e:
            # logger.error(f"Failed to capture images: {e}")
            # # Handle specific recovery or retry logic here if necessary
        # except IOError as e:
            # logger.error(f"File IO Error: {e}")
            # # Handle file access or permission errors
        # except Exception as e:
            # logger.error(f"Unexpected error: {e}")
            # # Handle other unexpected errors

        # # Adjust the sleep duration as needed, e.g., for a 1-hour interval, use sleep(3600)
        # sleep(3600)  # Sleep for 1 hour before the next capture cycle

if __name__ == "__main__":
    logger.info(f"Connecting to {BROKER} on port {PORT} with keep alive {KEEP_ALIVE_INTERVAL}")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(USERNAME, PASSWORD)
    client.connect(BROKER, PORT, KEEP_ALIVE_INTERVAL)

    # Start the PCB temperature publishing routine in a separate thread
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


    # publish_images_thread = threading.Thread(target=publish_images, args=(client,))
    # publish_images_thread.daemon = True
    # publish_images_thread.start()

    client.loop_forever()

