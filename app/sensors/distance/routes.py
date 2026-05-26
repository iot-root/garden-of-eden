from flask import Blueprint, request, jsonify
from app.lib.lib import check_sensor_guard, sensor_provider
from .distance import Distance as DistanceControl 

distance_blueprint = Blueprint('distance', __name__)
distance_control = None

@sensor_provider
def get_distance_control():
    global distance_control
    if distance_control is None:
        try:
            distance_control = DistanceControl()
        except Exception:
            return None
    return distance_control

check_sensor = check_sensor_guard(sensor=get_distance_control, sensor_name="Distance")

@distance_blueprint.route('', methods=['GET'])
@check_sensor
def get_distance():
    distance_value = get_distance_control().measure_once()
    return jsonify(distance=distance_value), 200
