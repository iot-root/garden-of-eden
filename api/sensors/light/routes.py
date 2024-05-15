from api.lib.lib import check_sensor_guard
from flask import Blueprint, request, jsonify
from .light import Light as LightControl  # Assuming you have a model for Light
from api.scheduler.scheduler import Scheduler

light_blueprint = Blueprint('light', __name__)
light_control = LightControl()

# Sensor Routes
@light_blueprint.route('/on', methods=['POST'])
def turn_on():
    light_control.on()
    return jsonify(message="Light turned on"), 200

@light_blueprint.route('/off', methods=['POST'])
def turn_off():
    light_control.off()
    return jsonify(message="Light turned off"), 200

@light_blueprint.route('/brightness', methods=['POST'])
def set_brightness():
    data = request.get_json()
    brightness_value = data.get('value', 50) 
    try:
        light_control.set_brightness(brightness_value)
        return jsonify(message=f"Light adjusted to {brightness_value}%"), 200
    except ValueError as e:
        return jsonify(message=str(e)), 400

@light_blueprint.route('/brightness', methods=['GET'])
def get_brightness():
    brightness_value = light_control.get_brightness()
    return jsonify(value=brightness_value), 200

# Schedule Routes
scheduler = Scheduler()

@light_blueprint.route('schedule/add', methods=['POST'])
def add():
    min = request.json['minutes']
    scheduler.add(min)
    return jsonify(msg='added'), 200

@light_blueprint.route('schedule/update', methods=['POST'])
def update():
    min = request.json['minutes']
    id = request.json['id']
    scheduler.update(id, min)
    return jsonify(msg='updated'), 200

@light_blueprint.route('schedule/delete', methods=['POST'])
def delete():
    id = request.json['id']
    scheduler.delete(id)
    return jsonify(msg='deleted'), 200

@light_blueprint.route('schedule/delete-all', methods=['POST'])
def deleteAll():
    scheduler.deleteAll()
    return jsonify(msg='deleted all'), 200

@light_blueprint.route('schedule/get-all', methods=['GET'])
def getAll():
    jobs = scheduler.getAll()
    return jsonify(jobs), 200