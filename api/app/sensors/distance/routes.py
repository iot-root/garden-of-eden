from flask import Blueprint, request, jsonify
from app.lib.lib import check_sensor_guard
from .distance import Distance as DistanceControl 

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

