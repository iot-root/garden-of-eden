from flask import Blueprint, jsonify, send_file
from app.lib.lib import check_sensor_guard
from app.sensors.temperature.temperature import AM2320Sensor
import os

sensor = AM2320Sensor()

temperature_blueprint = Blueprint('temperature', __name__)

@temperature_blueprint.route('', methods=['GET'])
def get_temperature():    
    try:
        return jsonify(value='{:.2f}'.format(sensor.get_temperature()))
    except Exception as e:
        return jsonify(error=str(e))

@temperature_blueprint.route('/logs', methods=['GET'])
def get_logs():
    LOG_DIR = '/var/log'
    LOG_FILE = os.path.join(LOG_DIR, 'temperature.log')

    try:
        if os.path.exists(LOG_FILE):
            return send_file(LOG_FILE, as_attachment=True)
        else:
            return jsonify({"error": "Temperature file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
