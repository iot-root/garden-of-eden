from flask import Blueprint, jsonify, send_file
from app.lib.lib import check_sensor_guard
from app.sensors.humidity.humidity import AM2320Sensor
import os

sensor = AM2320Sensor()

humidity_blueprint = Blueprint('humidity', __name__)

@humidity_blueprint.route('', methods=['GET'])
def get_humidity():    
    try:
        return jsonify(value='{:.2f}'.format(sensor.get_humidity()))
    except Exception as e:
        return jsonify(error=str(e))

@humidity_blueprint.route('/logs', methods=['GET'])
def get_logs():
    LOG_DIR = '/var/log'
    LOG_FILE = os.path.join(LOG_DIR, 'humidity.log')

    try:
        if os.path.exists(LOG_FILE):
            return send_file(LOG_FILE, as_attachment=True)
        else:
            return jsonify({"error": "Humidity file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
