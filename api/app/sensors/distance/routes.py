from flask import Blueprint, request, jsonify, send_file
from app.lib.lib import check_sensor_guard
from .distance import Distance as DistanceControl 
import os

distance_blueprint = Blueprint('distance', __name__)
distance_control = DistanceControl()

@distance_blueprint.route('', methods=['GET'])
def get_distance():
    try:
        distance_value = distance_control.measure_once()
        return jsonify(value=distance_value), 200
    except Exception as e:
        log(e)
        return jsonify(error=str(e)), 400

@distance_blueprint.route('/logs', methods=['GET'])
def get_logs():
    LOG_DIR = '/var/log'
    LOG_FILE = os.path.join(LOG_DIR, 'distance.log')

    try:
        if os.path.exists(LOG_FILE):
            return send_file(LOG_FILE, as_attachment=True)
        else:
            return jsonify({"error": "Log file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
