from app.lib.lib import check_sensor_guard, log
from flask import Blueprint, jsonify, send_file
from .pcb_temp import get_pcb_temperature
import os

pcb_temp_blueprint = Blueprint('pcb-temp', __name__)
check_sensor = check_sensor_guard(sensor=get_pcb_temperature, sensor_name='PCB Temp')

@pcb_temp_blueprint.route('', methods=['GET'])
def get_pcb_temp():
    try:
         return jsonify({"value": '{:.2f}'.format(get_pcb_temperature())})
    except Exception as e:
        log(e)
        return jsonify(error=str(e)), 400

@pcb_temp_blueprint.route('/logs', methods=['GET'])
def get_logs():
    LOG_DIR = '/var/log'
    LOG_FILE = os.path.join(LOG_DIR, 'pcb_temp.log')

    try:
        if os.path.exists(LOG_FILE):
            return send_file(LOG_FILE, as_attachment=True)
        else:
            return jsonify({"error": "PCB Temp file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
