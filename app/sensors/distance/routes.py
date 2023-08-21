from flask import Blueprint, request, jsonify
from .distance import Distance as DistanceControl  # Assuming you have a model for Light

distance_blueprint = Blueprint('distance', __name__)
distance_control = DistanceControl()

@distance_blueprint.route('/measure', methods=['GET'])
def get_speed():
    distance_value = distance_control.measure()
    return jsonify(distance=distance_value), 200

