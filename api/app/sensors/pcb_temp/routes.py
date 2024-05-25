from app.lib.lib import check_sensor_guard, log
from flask import Blueprint, jsonify
from .pcb_temp import get_pcb_temperature

pcb_temp_blueprint = Blueprint('pcb-temp', __name__)
check_sensor = check_sensor_guard(sensor=get_pcb_temperature, sensor_name='PCB Temp')

@pcb_temp_blueprint.route('', methods=['GET'])
def get_pcb_temp():
    try:
         return jsonify({"value": '{:.2f}'.format(get_pcb_temperature())})
    except Exception as e:
        log(e)
        return jsonify(error=str(e)), 400
