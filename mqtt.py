import threading
import logging
import paho.mqtt.client as mqtt
import json
from time import sleep
from config import USERNAME, PASSWORD, BROKER, PORT, KEEP_ALIVE_INTERVAL, BASE_TOPIC

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
from app.sensors.light.light import Light
from app.sensors.pump.pump import Pump
from app.sensors.pcb_temp.pcb_temp import get_pcb_temperature
from app.sensors.temperature.temperature import temperature_sensor
from app.sensors.humidity.humidity import humidity_sensor

# Initialize devices
pump = Pump()
light = Light()
brightness=50

def send_discovery_messages(client):
    # Config for Light
    #homeassistant/<component>/[<node_id>/]<object_id>/config.
    LIGHT_CONFIG_TOPIC = "homeassistant/light/gardyn/light/config"
    light_config_payload = {
        "name": "Gardyn Light",
        "unique_id": "gardyn_light",
        "platform": "mqtt",
        "state_topic": BASE_TOPIC + "/light/state",
        "command_topic": BASE_TOPIC + "/light/command",
        "brightness_state_topic": BASE_TOPIC + "/light/brightness/state",
        "brightness_command_topic": BASE_TOPIC + "/light/brightness/set",
        "brightness_scale": 100,
    }
    client.publish(LIGHT_CONFIG_TOPIC, json.dumps(light_config_payload), retain=True)

    #Config for Pump (as a switch with speed control, for example)
    PUMP_POWER_CONFIG_TOPIC = "homeassistant/switch/gardyn/pump_power/config"
    pump_config_payload = {
        "name": "Gardyn Pump Power",
        "unique_id": "gardyn_pump_power",
        # "platform": "mqtt",
        "state_topic": BASE_TOPIC + "/pump/state",
        "command_topic": BASE_TOPIC + "/pump/command"
    }
    client.publish(PUMP_POWER_CONFIG_TOPIC, json.dumps(pump_config_payload), retain=True)
    
    
    PUMP_SPEED_CONFIG_TOPIC = "homeassistant/number/gardyn/pump_speed/config"
    pump_config_payload = {
        "name": "Gardyn Pump Speed",
        "unique_id": BASE_TOPIC + "_pump_speed",
        "state_topic": BASE_TOPIC + "/pump/speed/state",
        "command_topic": BASE_TOPIC + "/pump/speed/set",
        "min": 0,
        "max": 100,
        "step": 1,
    }
    client.publish(PUMP_SPEED_CONFIG_TOPIC, json.dumps(pump_config_payload), retain=True)
    
    #Config for Temperature from PCB
    TEMP_PCB_CONFIG_TOPIC = "homeassistant/sensor/gardyn/pcb_temperature/config"
    temp_pcb_config_payload = {
        "name": "Gardyn PCB Temperature",
        "unique_id": BASE_TOPIC + "_pcb_temp",
        "state_topic": BASE_TOPIC + "/pcb/temperature",
        "unit_of_measurement": "°C",
        "device_class": "temperature"
    }
    client.publish(TEMP_PCB_CONFIG_TOPIC, json.dumps(temp_pcb_config_payload), retain=True)
    
    #Config for Temperature Sensor
    TEMP_TEMPERATURE_CONFIG_TOPIC = "homeassistant/sensor/gardyn/temperature/config"
    temp_pcb_config_payload = {
        "name": "Gardyn Temperature",
        "unique_id": BASE_TOPIC + "_temperature",
        "state_topic": BASE_TOPIC + "/temperature",
        "unit_of_measurement": "°C",
        "device_class": "temperature"
    }
    client.publish(TEMP_TEMPERATURE_CONFIG_TOPIC, json.dumps(temp_pcb_config_payload), retain=True)
    
    #Config for Humidity Sensor
    TEMP_HUMIDITY_CONFIG_TOPIC = "homeassistant/sensor/gardyn/humidity/config"
    temp_pcb_config_payload = {
        "name": "Gardyn Humidity",
        "unique_id": BASE_TOPIC + "_humidity",
        "state_topic": BASE_TOPIC + "/humidity",
        "unit_of_measurement": "%",
        "device_class": "humidity"
    }
    client.publish(TEMP_HUMIDITY_CONFIG_TOPIC, json.dumps(temp_pcb_config_payload), retain=True)

    # ... [similar configurations for other devices] ...

def on_connect(client, userdata, flags, rc, properties=None):
    logger.info(f"Connected with result code {rc}")
    client.subscribe(BASE_TOPIC + "/#")
    # client.subscribe(BASE_TOPIC + "/light/brightness/set")
    send_discovery_messages(client)

def on_message(client, userdata, msg):
    logger.debug(f"Message received on topic {msg.topic}: {msg.payload.decode()}")
    payload = msg.payload.decode("utf-8")
    logger.debug(f"Raw payload: '{payload}'")
    topic = msg.topic.split("/")[-1]
    
    
    # pump commands
    if msg.topic == BASE_TOPIC + "/pump/command":
        if payload.upper() == "ON":
            logger.info(f"/pump/state ON")
            pump.on()
            client.publish(BASE_TOPIC + "/pump/state", "ON")
        elif payload.upper() == "OFF":
            logger.info(f"/pump/state off")
            pump.off()
            client.publish(BASE_TOPIC + "/pump/state", "OFF")
    elif msg.topic == BASE_TOPIC + "/pump/speed/set":
        pump.set_speed(int(payload))
        logger.info(f"/pump/speed/state {payload}")
        client.publish(BASE_TOPIC + "/pump/speed/state", payload)

    # light commands
    if msg.topic == BASE_TOPIC + "/light/command":
        if payload.upper() == "ON":
            global brightness
            light.set_duty_cycle(brightness)
            logger.info(f"/light/state ON")
            client.publish(BASE_TOPIC + "/light/state", "ON")
        elif payload.upper() == "OFF":
            light.off()
            logger.info(f"/light/state OFF")
            client.publish(BASE_TOPIC + "/light/state", "OFF")
    elif msg.topic == BASE_TOPIC + "/light/brightness/set":
        brightness = int(payload)
        light.set_duty_cycle(brightness)
        logger.info(f"/light/brightness/state {brightness}")
        client.publish(BASE_TOPIC + "/light/brightness/state", str(brightness))

def publish_pcb_temperature(client):
    while True:
        try:
            pcb_temp = get_pcb_temperature()
            logger.info(f"Publishing PCB Temperature: {pcb_temp:.2f}°C")
            client.publish(BASE_TOPIC + "/pcb/temperature", f"{pcb_temp:.2f}")
        except Exception as e:
            logger.error(f"Failed to read or publish PCB temperature: {e}")
        sleep(60)  # Publish temperature every 60 seconds
        
def publish_temperature(client):
    while True:
        try:
            temperature = temperature_sensor.get_value()
            logger.info(f"Publishing PCB Temperature: {temperature:.2f}°C")
            client.publish(BASE_TOPIC + "/temperature", f"{temperature:.2f}")
        except Exception as e:
            logger.error(f"Failed to read or publish PCB temperature: {e}")
        sleep(60)  # Publish temperature every 60 seconds
        
def publish_humidity(client):
    while True:
        try:
            humidity = humidity_sensor.get_value()
            logger.info(f"Publishing PCB Temperature: {humidity:.2f}%")
            client.publish(BASE_TOPIC + "/humidity", f"{humidity:.2f}")
        except Exception as e:
            logger.error(f"Failed to read or publish PCB temperature: {e}")
        sleep(60)  # Publish temperature every 60 seconds

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
    
    client.loop_forever()
    