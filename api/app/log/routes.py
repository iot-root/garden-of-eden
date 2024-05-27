from flask import Blueprint, jsonify
from app.lib.lib import log
import subprocess
import os

log_blueprint = Blueprint('log', __name__)

@log_blueprint.route('', methods=['POST'])
def capture_logs():
    try:
        # Define the script path
        script_path = os.path.join(os.getcwd(), '../../bin/api/log-sensor-data.sh')
        print(script_path)
        # Execute the script
        result = subprocess.run([script_path], capture_output=True, text=True, shell=True)
        
        # Check for errors
        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500

        return jsonify({"output": result.stdout})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
