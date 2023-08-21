from flask import Blueprint, jsonify
from .pcb_temp import get_pcb_temperature

pcb_temp_blueprint = Blueprint('pcb_temp', __name__)

@pcb_temp_blueprint.route('', methods=['GET'])
def get_pcb_temp():
    temperature = get_pcb_temperature()
    return jsonify({"pcb-temp": temperature})
