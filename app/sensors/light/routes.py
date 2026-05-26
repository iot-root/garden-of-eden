from app.lib.lib import check_sensor_guard, sensor_provider
from flask import Blueprint, request, jsonify
from .light import Light as LightControl  # Assuming you have a model for Light

light_blueprint = Blueprint('light', __name__)
light_control = None

@sensor_provider
def get_light_control():
    global light_control
    if light_control is None:
        try:
            light_control = LightControl()
        except Exception:
            return None
    return light_control

check_sensor = check_sensor_guard(sensor=get_light_control, sensor_name='Light')

@light_blueprint.route('/on', methods=['POST'])
@check_sensor
def turn_on():
    get_light_control().on()
    return jsonify(message="Light turned on"), 200

@light_blueprint.route('/off', methods=['POST'])
@check_sensor
def turn_off():
    get_light_control().off()
    return jsonify(message="Light turned off"), 200

@light_blueprint.route('/brightness', methods=['POST'])
@check_sensor
def set_brightness():
    data = request.get_json()
    brightness_value = data.get('value', 50) 
    try:
        get_light_control().set_brightness(brightness_value)
        return jsonify(message=f"Light adjusted to {brightness_value}%"), 200
    except ValueError as e:
        return jsonify(message=str(e)), 400

@light_blueprint.route('/brightness', methods=['GET'])
@check_sensor
def get_brightness():
    brightness_value = get_light_control().get_brightness()
    return jsonify(value=brightness_value), 200
