from flask import Blueprint, request, jsonify
from api.lib.lib import check_sensor_guard
from .pump import Pump as PumpControl 
from .pump_power import fetch_ina219_data

pump_blueprint = Blueprint('pump', __name__)
pump_control = PumpControl()

@pump_blueprint.route('/on', methods=['POST'])
def turn_on():
    pump_control.on()
    return jsonify(message="Pump turned on"), 200

@pump_blueprint.route('/off', methods=['POST'])
def turn_off():
    pump_control.off()
    return jsonify(message="Pump turned off"), 200

@pump_blueprint.route('/speed', methods=['POST'])
def adjust_speed():
    data = request.get_json()
    speed_value = data.get('value', 30)  # default to 30 percent
    try:
        pump_control.set_speed(speed_value)
        return jsonify(message=f"Pump adjusted to {speed_value}% speed"), 200
    except ValueError as e:
        return jsonify(message=str(e)), 400

@pump_blueprint.route('/speed', methods=['GET'])
def get_speed():
    current_speed = pump_control.get_speed()
    return jsonify(value=current_speed), 200

@pump_blueprint.route('/stats', methods=['GET'])
def get_pump_data():
    data = fetch_ina219_data()
    return jsonify(data)
