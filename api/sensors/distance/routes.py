from flask import Blueprint, request, jsonify
from api.lib.lib import check_sensor_guard
from .distance import Distance as DistanceControl 

distance_blueprint = Blueprint('distance', __name__)
distance_control = DistanceControl()

@distance_blueprint.route('', methods=['GET'])
def get_distance():
    distance_value = distance_control.measure_once()
    return jsonify(distance=distance_value), 200

