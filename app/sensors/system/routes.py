from flask import Blueprint, jsonify

import config
from app.lib.hardware import detect_model, lower_camera_enabled, profile_for

system_blueprint = Blueprint("system", __name__)


@system_blueprint.route("", methods=["GET"])
def get_system():
    """Report identity, version, and the detected hardware model/profile."""
    model = detect_model()
    lower_camera = lower_camera_enabled(model)
    profile = dict(profile_for(model))
    profile["lower_camera"] = lower_camera
    profile["cameras"] = 2 if lower_camera else 1
    return jsonify(
        {
            "identifier": config.IDENTIFIER,
            "version": config.VERSION,
            "model": model,
            "profile": profile,
            "sensor_type": config.SENSOR_TYPE,
            "water_low_cm": config.WATER_LOW_CM,
            "pump_max_run_seconds": config.MAX_PUMP_RUN_SECONDS,
        }
    )
