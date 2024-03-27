import logging
import paho.mqtt.client as mqtt
import json
from time import sleep
from config import USERNAME, PASSWORD, BROKER, PORT, KEEP_ALIVE_INTERVAL, BASE_TOPIC

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
from app.sensors.light.light import Light

# from app.sensors.pump.pump import Pump

# from app.sensors.pcb_temp import PCB
# from app.sensors import Temperature
# from app.sensors import Humidity

# Initialize devices
# pump = Pump()
light = Light()
brightness=50

def send_discovery_messages(client):
    # Config for Light
    LIGHT_CONFIG_TOPIC = "homeassistant/light/iot_device/light/config"
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

    # Config for Pump (as a switch with speed control, for example)
    # PUMP_CONFIG_TOPIC = "homeassistant/switch/iot_device/pump/config"
    # pump_config_payload = {
    #     "name": "IoT Pump",
    #     "state_topic": BASE_TOPIC + "pump/state",
    #     "command_topic": BASE_TOPIC + "pump/command",
    #     "speed_state_topic": BASE_TOPIC + "pump/speed/state",
    #     "speed_command_topic": BASE_TOPIC + "pump/speed/set"
    # }
    # client.publish(PUMP_CONFIG_TOPIC, json.dumps(pump_config_payload), retain=True)

    # Config for Temperature from PCB
    # TEMP_PCB_CONFIG_TOPIC = "homeassistant/sensor/iot_device/pcb_temperature/config"
    # temp_pcb_config_payload = {
    #     "name": "PCB Temperature",
    #     "state_topic": BASE_TOPIC + "pcb/temperature",
    #     "unit_of_measurement": "°C",
    #     "device_class": "temperature"
    # }
    # client.publish(TEMP_PCB_CONFIG_TOPIC, json.dumps(temp_pcb_config_payload), retain=True)

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
    
    

    # if "pump" in msg.topic: 
    #     if topic == "set_speed":
    #         pump.set_speed(int(payload))
    #         client.publish(BASE_TOPIC + "/pump/speed/state", payload)
    #     elif topic == "on":
    #         pump.on()
    #         client.publish(BASE_TOPIC + "/pump/state", "ON")
    #     elif topic == "off":
    #         pump.off()
    #         client.publish(BASE_TOPIC + "/pump/state", "OFF")

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

if __name__ == "__main__":
    logger.info(f"Connecting to {BROKER} on port {PORT} with keep alive {KEEP_ALIVE_INTERVAL}")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(USERNAME, PASSWORD)
    client.connect(BROKER, PORT, KEEP_ALIVE_INTERVAL)
    client.loop_forever()
    