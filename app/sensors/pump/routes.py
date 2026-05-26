from flask import Blueprint, request, jsonify
from app.lib.lib import check_sensor_guard, sensor_provider
from .pump import Pump as PumpControl 
from .pump_power import fetch_ina219_data

pump_blueprint = Blueprint('pump', __name__)
pump_control = None

@sensor_provider
def get_pump_control():
    global pump_control
    if pump_control is None:
        try:
            pump_control = PumpControl()
        except Exception:
            return None
    return pump_control

check_sensor = check_sensor_guard(sensor=get_pump_control, sensor_name='Pump')

@pump_blueprint.route('/on', methods=['POST'])
@check_sensor
def turn_on():
    get_pump_control().on()
    return jsonify(message="Pump turned on!"), 200

@pump_blueprint.route('/off', methods=['POST'])
@check_sensor
def turn_off():
    get_pump_control().off()
    return jsonify(message="Pump turned off!"), 200

@pump_blueprint.route('/speed', methods=['POST'])
@check_sensor
def adjust_speed():
    data = request.get_json()
    speed_value = data.get('value', 30)  # default to 30 percent
    try:
        get_pump_control().set_speed(speed_value)
        return jsonify(message=f"Pump adjusted to {speed_value}% speed!"), 200
    except ValueError as e:
        return jsonify(message=str(e)), 400

@pump_blueprint.route('/speed', methods=['GET'])
@check_sensor
def get_speed():
    current_speed = get_pump_control().get_speed()
    return jsonify(value=current_speed), 200

@pump_blueprint.route('/stats', methods=['GET'])
@check_sensor
def get_pump_data():
    data = fetch_ina219_data()
    return jsonify(data)
