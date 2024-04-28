from flask import Blueprint, request, jsonify
from app.lib.lib import check_sensor_guard
from .distance import Distance as DistanceControl 

distance_blueprint = Blueprint('distance', __name__)
distance_control = DistanceControl()
check_sensor = check_sensor_guard(sensor=distance_control, sensor_name="Distance")

@distance_blueprint.route('', methods=['GET'])
@check_sensor
def get_distance():
    distance_value = distance_control.measure_once()
    return jsonify(distance=distance_value), 200

