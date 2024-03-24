#!/usr/bin/env python3
from app import create_app
from flask_cors import CORS
import paho.mqtt.client as mqtt

app = create_app('default')
CORS(app)

# MQTT Configuration
BROKER = 'your_mqtt_broker_address'
PORT = 1883

# Mapping of REST API endpoints to MQTT topics
ENDPOINT_TO_TOPIC = {
    "motor": "devices/motor",
    "light": "devices/light",
    "humidity": "devices/humidity",
    "distance": "devices/distance"
}

def publish_to_mqtt(topic, data):
    """Helper function to publish data to an MQTT topic."""
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    client.publish(topic, data)
    client.disconnect()

@app.route('/<device>', methods=['POST'])
def handle_device(device):
    """Endpoint to handle different devices."""
    if device not in ENDPOINT_TO_TOPIC:
        return jsonify({"error": "Invalid device"}), 400

    data = request.data.decode('utf-8')
    mqtt_topic = ENDPOINT_TO_TOPIC[device]
    publish_to_mqtt(mqtt_topic, data)

    return jsonify({"message": f"Data for {device} published to MQTT"}), 200


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
    # app.run(host='0.0.0.0', port=5000)
