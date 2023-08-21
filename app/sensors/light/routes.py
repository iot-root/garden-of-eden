from flask import Blueprint, request, jsonify
from .light import Light as LightControl  # Assuming you have a model for Light

light_blueprint = Blueprint('light', __name__)
light_control = LightControl()

@light_blueprint.route('/on', methods=['POST'])
def turn_on():
    light_control.on()
    return jsonify(message="Light turned on!"), 200

@light_blueprint.route('/off', methods=['POST'])
def turn_off():
    light_control.off()
    return jsonify(message="Light turned off!"), 200

@light_blueprint.route('/brightness', methods=['POST'])
def adjust_brightness():
    data = request.get_json()
    brightness_value = data.get('value', 50) 
    try:
        light_control.set_brightness(brightness_value)
        return jsonify(message=f"Light adjusted to {brightness_value}%"), 200
    except ValueError as e:
        return jsonify(message=str(e)), 400

@light_blueprint.route('/brightness', methods=['GET'])
def get_speed():
    brightness_value = light_control.get_brightness()
    return jsonify(value=brightness_value), 200
