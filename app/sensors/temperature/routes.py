from flask import Blueprint, jsonify
from app.lib.lib import check_sensor_guard, sensor_provider
from .temperature import get_temperature_sensor as load_temperature_sensor

temperature_blueprint = Blueprint('temperature', __name__)

@sensor_provider
def get_temperature_sensor():
    return load_temperature_sensor()

check_sensor = check_sensor_guard(sensor=get_temperature_sensor, sensor_name='Temperature')

@temperature_blueprint.route('', methods=['GET'])
@check_sensor
def get_temperature():    
    return jsonify(temperature='{:.2f}'.format(get_temperature_sensor().read()))
