import paho.mqtt.client as mqtt
import json
from config import USERNAME, PASSWORD, BROKER, PORT, KEEP_ALIVE_INTERVAL, BASE_TOPIC
# from app.sensors.pump.pump import Pump
# from app.sensors.light.light import Light
# from app.sensors.pcb_temp import PCB
# from app.sensors import Temperature
# from app.sensors import Humidity

# Initialize devices
# pump = Pump()
# light = Light()

def send_discovery_messages(client):
    # Config for Light
    LIGHT_CONFIG_TOPIC = "homeassistant/light/iot_device/light/config"
    light_config_payload = {
        "name": "IoT Light",
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
    print(f"Connected with result code {rc}")
    client.subscribe(BASE_TOPIC + "/command/#")
    send_discovery_messages(client)

def on_message(client, userdata, msg):
    print("Message received: " + str(msg.payload.decode()))
    payload = msg.payload.decode("utf-8")
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

    if "light" in msg.topic:
        if topic == "set_brightness":
            # light.set_brightness(int(payload))
            client.publish(BASE_TOPIC + "/light/brightness/state", payload)
        elif topic == "on":
            # light.on()
            client.publish(BASE_TOPIC + "/light/state", "ON")
        elif topic == "off":
            # light.off()
            client.publish(BASE_TOPIC + "/light/state", "OFF")

    # if "temperature" in msg.topic:
    #     if topic == "set_brightness":
    #         light.set_brightness(int(payload))
    #         client.publish(BASE_TOPIC + "/light/brightness/state", payload)
    #     elif topic == "on":
    #         light.on()
    #         client.publish(BASE_TOPIC + "/light/state", "ON")
    #     elif topic == "off":
    #         light.off()
    #         client.publish(BASE_TOPIC + "/light/state", "OFF")



if __name__ == "__main__":
    print(f"{BASE_TOPIC} {BROKER} {PORT} {KEEP_ALIVE_INTERVAL}")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(USERNAME, PASSWORD)
    client.connect(BROKER, PORT, KEEP_ALIVE_INTERVAL)
    client.loop_forever()
