from api.lib.lib import check_sensor_guard
from flask import Blueprint, request, jsonify
from .light import Light as LightControl  # Assuming you have a model for Light
from api.scheduler.scheduler import lightScheduler
from api.lib.lib import log

light_blueprint = Blueprint('light', __name__)
light_control = LightControl()

# Sensor Routes
@light_blueprint.route('/on', methods=['POST'])
def turn_on():
    try:
        light_control.on()
        return jsonify(message="Light turned on"), 200
    except Exception as e:
        log(e)
        return jsonify(error=str(e)), 400

@light_blueprint.route('/off', methods=['POST'])
def turn_off():
    try:
        light_control.off()
        return jsonify(message="Light turned off"), 200
    except Exception as e:
        log(e)
        return jsonify(error=str(e)), 400

@light_blueprint.route('/brightness', methods=['POST'])
def set_brightness():
    data = request.get_json()
    brightness_value = data.get('value') 
    try:
        light_control.set_brightness(brightness_value)
        return jsonify(message=f"Light adjusted to {brightness_value}%"), 200
    except Exception as e:
        log(e)
        return jsonify(error=str(e)), 400

@light_blueprint.route('/brightness', methods=['GET'])
def get_brightness():
    try:
        brightness_value = light_control.get_brightness()
        return jsonify(value=brightness_value), 200
    except Exception as e:
        log(e)
        return jsonify(error=str(e)), 400

# Schedule Routes
@light_blueprint.route('schedule/add', methods=['POST'])
def add():
    min = request.json['minutes']
    hour = request.json['hour']
    day = request.json['day']
    brightness = request.json['brightness']
    state = request.json['state']
   
    try:
        response = lightScheduler.add(min, hour, day, state=state, brightness=brightness)
        return jsonify(response), 200
    except Exception as e:
        log(e)
        return jsonify(error=str(e)), 400

@light_blueprint.route('schedule/update', methods=['POST'])
def update():
    min = request.json['minutes']
    hour = request.json['hour']
    day = request.json['day']
    brightness = request.json['brightness']
    state = request.json['state']
    id = request.json['id']

    try:
        response = lightScheduler.update(id, min, hour, day, state=state, brightness=brightness)
        return jsonify(response), 200
    except Exception as e:
        log(e)
        return jsonify(error=str(e)), 400
