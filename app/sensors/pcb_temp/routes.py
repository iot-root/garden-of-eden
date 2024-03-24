from flask import Blueprint, jsonify
from .pcb_temp import get_pcb_temperature

pcb_temp_blueprint = Blueprint('pcb-temp', __name__)

@pcb_temp_blueprint.route('', methods=['GET'])
def get_pcb_temp():
    return jsonify({"pcb-temp": '{:.2f}'.format(get_pcb_temperature())})
