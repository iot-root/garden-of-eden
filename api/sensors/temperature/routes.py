from flask import Blueprint, jsonify
from api.lib.lib import check_sensor_guard
from .temperature import temperature_sensor

temperature_blueprint = Blueprint('temperature', __name__)
check_sensor = check_sensor_guard(sensor=temperature_sensor, sensor_name='Temperature')

@temperature_blueprint.route('', methods=['GET'])
@check_sensor
def get_temperature():    
    try:
        return jsonify(temperature='{:.2f}'.format(temperature_sensor.get_value()))
    except Exception as e:
        return jsonify(error=str(e))