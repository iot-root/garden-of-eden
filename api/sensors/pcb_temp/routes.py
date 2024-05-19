from api.lib.lib import check_sensor_guard
from flask import Blueprint, jsonify
from .pcb_temp import get_pcb_temperature

pcb_temp_blueprint = Blueprint('pcb-temp', __name__)
check_sensor = check_sensor_guard(sensor=get_pcb_temperature, sensor_name='PCB Temp')

@pcb_temp_blueprint.route('', methods=['GET'])
def get_pcb_temp():
    try:
         return jsonify({"pcb-temp": '{:.2f}'.format(get_pcb_temperature())})
    except ValueError as e:
        return jsonify(message=str(e)), 400
