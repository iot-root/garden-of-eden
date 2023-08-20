from flask import Blueprint, request, jsonify
from .pump import Pump as PumpControl # Assuming you have a model for Pump

pump = Blueprint('pump', __name__)
pump_control = PumpControl()

@pump.route('/on', methods=['POST'])
def turn_on():
    pump_control.on()
    return jsonify(message="Pump turned on!"), 200

@pump.route('/off', methods=['POST'])
def turn_off():
    pump_control.off()
    return jsonify(message="Pump turned off!"), 200

@pump.route('/speed', methods=['POST'])
def adjust_speed():
    data = request.get_json()
    speed_value = data.get('value', 30)  # default to 30 percent
    try:
        pump_control.set_speed(speed_value)
        return jsonify(message=f"Pump adjusted to {speed_value}% speed!"), 200
    except ValueError as e:
        return jsonify(message=str(e)), 400

@pump.route('/speed', methods=['GET'])
def get_speed():
    current_speed = pump_control.get_speed()
    return jsonify(value=current_speed), 200

