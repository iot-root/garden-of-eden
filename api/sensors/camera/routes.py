from flask import Blueprint, request, jsonify
from api.lib.lib import check_sensor_guard, log
from .camera import Camera

camera_blueprint = Blueprint('camera', __name__)
camera_control = Camera()

@camera_blueprint.route('/capture', methods=['GET'])
def capture_images():
    try:
        response = camera_control.capture_images()
        # return capture images
        return jsonify(message=response), 200
    except Exception as e:
        log(e)
        return jsonify(error=str(e)), 400

@camera_blueprint.route('/get', methods=['GET'])
def get_images():
    try:
        response = camera_control.get_images()
        # return capture images in tmp
        return jsonify(message=response), 200
    except Exception as e:
        log(e)
        return jsonify(error=str(e)), 400