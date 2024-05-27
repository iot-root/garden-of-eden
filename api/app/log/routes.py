from flask import Blueprint, jsonify, request
from app.lib.lib import log
import subprocess
import os
from app.scheduler.scheduler import logScheduler

log_blueprint = Blueprint('log', __name__)

@log_blueprint.route('', methods=['POST'])
def capture_logs():
    try:
        # Define the script path
        script_path = os.path.join(os.getcwd(), 'bin/api/log-sensor-data.sh')
        print(script_path)
        # Execute the script
        result = subprocess.run([script_path], capture_output=True, text=True, shell=True)
        
        # Check for errors
        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500

        return jsonify({"message": "Logging successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@log_blueprint.route('/schedule/add', methods=['POST'])
def add_schedule():
    try:
        min = request.json['minutes']
        hour = request.json['hour']
        day = request.json['day']
        logScheduler.add(min, hour, day)
        return jsonify({"message": "Added schedule"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
