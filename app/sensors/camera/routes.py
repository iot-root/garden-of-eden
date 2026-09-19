import logging
import os

from flask import Blueprint, jsonify, send_file

import config

from . import camera

logger = logging.getLogger(__name__)

camera_blueprint = Blueprint("camera", __name__)


def _serve(capture_fn, path):
    try:
        capture_fn()
    except FileNotFoundError:
        return jsonify(error="fswebcam not installed on this host"), 503
    except Exception as exc:
        logger.error("Camera capture failed: %s", exc)
        return jsonify(error=f"camera capture failed: {exc}"), 503
    return send_file(path, mimetype="image/jpeg")


@camera_blueprint.route("/upper", methods=["GET"])
def upper():
    return _serve(camera.capture_upper, config.UPPER_IMAGE_PATH)


@camera_blueprint.route("/lower", methods=["GET"])
def lower():
    return _serve(camera.capture_lower, config.LOWER_IMAGE_PATH)


@camera_blueprint.route("/timelapse/<cam>", methods=["GET"])
def get_timelapse(cam):
    if cam not in camera.CAMERAS:
        return jsonify(error="unknown camera"), 400
    path = camera.timelapse_path(cam)
    if not os.path.exists(path):
        return jsonify(error="no timelapse yet — generate one"), 404
    return send_file(path, mimetype="video/mp4")


@camera_blueprint.route("/timelapse/<cam>", methods=["POST"])
def make_timelapse(cam):
    if cam not in camera.CAMERAS:
        return jsonify(error="unknown camera"), 400
    try:
        camera.generate_timelapse(cam)
    except FileNotFoundError as exc:
        return jsonify(error=str(exc)), 404
    except Exception as exc:
        logger.error("Timelapse generation failed: %s", exc)
        return jsonify(error=f"generation failed: {exc}"), 503
    return jsonify(message=f"{cam} timelapse generated"), 200
