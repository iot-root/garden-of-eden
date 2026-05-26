from flask import Blueprint, jsonify
from app.lib.lib import check_sensor_guard, sensor_provider
from .humidity import get_humidity_sensor as load_humidity_sensor

humidity_blueprint = Blueprint('humidity', __name__)

@sensor_provider
def get_humidity_sensor():
    return load_humidity_sensor()

check_sensor = check_sensor_guard(sensor=get_humidity_sensor, sensor_name='Humidity')

@humidity_blueprint.route('', methods=['GET'])
@check_sensor
def get_humidity():
    return jsonify(humidity='{:.2f}'.format(get_humidity_sensor().read()))
