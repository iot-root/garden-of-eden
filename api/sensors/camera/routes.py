from flask import Blueprint, request, jsonify, send_from_directory
from api.lib.lib import check_sensor_guard, log
from .camera import Camera

camera_blueprint = Blueprint('camera', __name__)
camera_control = Camera()

@camera_blueprint.route('/capture', methods=['GET'])
def capture_images():
    try:
        response = camera_control.capture_images()
        # return capture images
        return response
    except Exception as e:
        log(e)
        return jsonify(error=str(e)), 400

@camera_blueprint.route('/get', methods=['POST'])
def get_image():
    data = request.get_json()
    filename = data.get('value')
    return camera_control.get_image(filename)

@camera_blueprint.route('/list-images', methods=['GET'])
def list_images():
    return camera_control.list_images()

@camera_blueprint.route('/delete', methods=['POST'])
def list_images():
    data = request.get_json()
    filename = data.get('value')
    return camera_control.delete_image(filename)