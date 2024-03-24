from flask import Blueprint, jsonify
from .temperature import temperature_sensor

temperature_blueprint = Blueprint('temperature', __name__)

@temperature_blueprint.route('', methods=['GET'])
def get_temperature():
    return jsonify(temperature='{:.2f}'.format(temperature_sensor.get_value()))
