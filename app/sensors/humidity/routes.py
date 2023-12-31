from flask import Blueprint, jsonify
from .humidity import humidity_sensor

humidity_blueprint = Blueprint('humidity', __name__)

@humidity_blueprint.route('', methods=['GET'])
def get_humidity():
    return jsonify(humidity=humidity_sensor.get_value())
