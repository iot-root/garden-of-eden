from flask import Blueprint, jsonify
from sensors import temp_sensor

bp = Blueprint('temperature', __name__)

@bp.route('', methods=['GET'])
def temperature():
    return jsonify(temperature=temp_sensor.get_value())
