from app.lib.lib import check_sensor_guard
from flask import Blueprint, request, jsonify
from .light import Light as LightControl  # Assuming you have a model for Light

light_blueprint = Blueprint('light', __name__)
light_control = LightControl()
check_sensor = check_sensor_guard(sensor=light_control, sensor_name='Light')

@light_blueprint.route('/on', methods=['POST'])
@check_sensor
def turn_on():
    light_control.on()
    return jsonify(message="Light turned on"), 200

@light_blueprint.route('/off', methods=['POST'])
@check_sensor
def turn_off():
    light_control.off()
    return jsonify(message="Light turned off"), 200

@light_blueprint.route('/brightness', methods=['POST'])
@check_sensor
def set_brightness():
    data = request.get_json()
    brightness_value = data.get('value', 50) 
    try:
        light_control.set_brightness(brightness_value)
        return jsonify(message=f"Light adjusted to {brightness_value}%"), 200
    except ValueError as e:
        return jsonify(message=str(e)), 400

@light_blueprint.route('/brightness', methods=['GET'])
@check_sensor
def get_brightness():
    brightness_value = light_control.get_brightness()
    return jsonify(value=brightness_value), 200
