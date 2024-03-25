#!/usr/bin/env python3
import logging
from flask import jsonify, request
from app import create_app
from flask_cors import CORS
#import paho.mqtt.client as mqtt
#from config import BROKER, PORT, KEEP_ALIVE_INTERVAL, BASE_TOPIC, USERNAME, PASSWORD

# Configure logging
#logging.basicConfig(level=logging.INFO)
#logging.basicConfig(filename='test.log', level=logging.DEBUG)

#logger = logging.getLogger(__name__)

app = create_app('default')
CORS(app)

# Mapping of REST API endpoints to MQTT topics
#ENDPOINT_TO_TOPIC = {
#    "motor": "devices/motor",
#    "light": "devices/light",
#    "humidity": "devices/humidity",
#    "distance": "devices/distance"
#}
#
#def publish_to_mqtt(topic, data):
#    """Helper function to publish data to an MQTT topic."""
#    # client = mqtt.Client(client_id="your_client_id", clean_session=True, protocol=mqtt.MQTTv311)
#    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
#    client.username_pw_set(USERNAME, PASSWORD)
#    client.connect(BROKER, PORT, 60)
##    client.enable_logger(logging.getLogger(__name__))
#    client.publish(topic, data)
#    client.disconnect()
#
#@app.route('/<device>/<action>', methods=['POST'])
#def handle_device(device):
#    """Endpoint to handle different devices."""
#    printf("triggered mqtt")
#    logger.info(f"mqtt trigger {device} {action}")
#    if device not in ENDPOINT_TO_TOPIC:
#        logger.error(f"Invalid device: {device}")
#        return jsonify({"error": "Invalid device"}), 400
#
#    data = request.data.decode('utf-8')
#    mqtt_topic = ENDPOINT_TO_TOPIC[device]
#    logger.info(f"Publishing data to MQTT topic: {mqtt_topic}")
#    publish_to_mqtt(mqtt_topic, data)
#    logger.info(f"Data for {device} published to MQTT")
#
#    return jsonify({"message": f"Data for {device} published to MQTT"}), 200
#
#@app.route('/<sensor>/<action>', methods=['POST'])
#def test_route(sensor):
#    return f"Received POST request {sensor} {action}"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
