from flask import Blueprint, request, jsonify, send_file
from app.lib.lib import check_sensor_guard, log
from .pump import Pump as PumpControl 
from .pump_power import fetch_ina219_data
from app.scheduler.scheduler import pumpScheduler
import logging
import os

pump_blueprint = Blueprint('pump', __name__)
pump_control = PumpControl()

@pump_blueprint.route('/on', methods=['POST'])
def turn_on():
    try:
        pump_control.on()
        return jsonify(message="Pump turned on"), 200
    except Exception as e:
        log(e)
        return jsonify(error=str(e))

@pump_blueprint.route('/off', methods=['POST'])
def turn_off():
    try:
        pump_control.off()
        return jsonify(message="Pump turned off"), 200
    except Exception as e:
        log(e)
        return jsonify(error=str(e))

@pump_blueprint.route('/speed', methods=['POST'])
def adjust_speed():
    data = request.get_json()
    speed_value = data.get('value', 30)  # default to 30 percent
    try:
        pump_control.set_speed(speed_value)
        return jsonify(message=f"Pump adjusted to {speed_value}% speed"), 200
    except Exception as e:
        return jsonify(error=str(e)), 400

@pump_blueprint.route('/speed', methods=['GET'])
def get_speed():
    try:
        current_speed = pump_control.get_speed()
        return jsonify(value=current_speed), 200
    except Exception as e:
        return jsonify(error=str(e)), 400

@pump_blueprint.route('/stats', methods=['GET'])
def get_pump_data():
    try:
        data = fetch_ina219_data()
        if (data.get('error', False)):
            return jsonify(data=data), 400
        return jsonify(data=data), 200
    except Exception as e:
        return jsonify(error=str(e)), 400


# Schedule Routes
@pump_blueprint.route('schedule/add', methods=['POST'])
def add():
    min = request.json['minutes']
    hour = request.json['hour']
    day = request.json['day']
    speed = request.json['speed']
    state = request.json['state']
   
    try:
        response = pumpScheduler.add(min, hour, day, state=state, speed=speed)
        return jsonify(response), 200
    except Exception as e:
        return jsonify(error=str(e)), 400


@pump_blueprint.route('schedule/update', methods=['POST'])
def update():
    min = request.json['minutes']
    hour = request.json['hour']
    day = request.json['day']
    speed = request.json['speed']
    state = request.json['state']
    id = request.json['id']
    
    try:
        response = pumpScheduler.update(id, min, hour, day, state=state, speed=speed)
        return jsonify(response), 200
    except Exception as e:
        return jsonify(error=str(e)), 400
    
@pump_blueprint.route('speed/logs', methods=['GET'])
def get_speed_logs():
    LOG_DIR = '/var/log'
    LOG_FILE = os.path.join(LOG_DIR, 'pump_speed.log')

    try:
        if os.path.exists(LOG_FILE):
            return send_file(LOG_FILE, as_attachment=True)
        else:
            return jsonify({"error": "Pump Speed file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pump_blueprint.route('stats/logs', methods=['GET'])
def get_stats_logs():
    LOG_DIR = '/var/log'
    LOG_FILE = os.path.join(LOG_DIR, 'pump_stats.log')

    try:
        if os.path.exists(LOG_FILE):
            return send_file(LOG_FILE, as_attachment=True)
        else:
            return jsonify({"error": "Pump Stats file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
