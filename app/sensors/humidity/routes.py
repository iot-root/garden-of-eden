from flask import Blueprint, jsonify
from .humidity import humidity_sensor

bp = Blueprint('humidity_routes', __name__)

@bp.route('/humidity', methods=['GET'])
def humidity():
    return jsonify(humidity=humidity_sensor.get_value())
