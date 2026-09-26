import logging

from flask import Blueprint, jsonify, request

import config
from app.lib import settings
from app.lib.hardware import detect_model, lower_camera_enabled, profile_for

logger = logging.getLogger(__name__)

system_blueprint = Blueprint("system", __name__)


def _system_body():
    model = detect_model()
    lower_camera = lower_camera_enabled(model)
    profile = dict(profile_for(model))
    profile["lower_camera"] = lower_camera
    profile["cameras"] = 2 if lower_camera else 1
    return {
        "identifier": config.IDENTIFIER,
        "version": config.VERSION,
        "model": model,
        "model_source": settings.describe_source(),
        "model_override": settings.get_model_override(),
        "available_models": settings.available_models(),
        "profile": profile,
        "sensor_type": config.SENSOR_TYPE,
        "water_low_cm": config.WATER_LOW_CM,
        "pump_max_run_seconds": config.MAX_PUMP_RUN_SECONDS,
    }


@system_blueprint.route("", methods=["GET"])
def get_system():
    """Report identity, version, and the detected hardware model/profile."""
    return jsonify(_system_body())


@system_blueprint.route("/model", methods=["POST"])
def set_model():
    """Pin the hardware model from the web UI, or pass "auto" to undo it.

    The choice is validated against the known models and persisted outside
    ``.env``, so it survives a reboot without rewriting the credentials file.
    """
    data = request.get_json(silent=True) or {}
    requested = data.get("model", settings.AUTO)
    try:
        applied = settings.set_model_override(requested)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    except OSError as exc:  # unwritable state dir, full disk
        logger.error("Could not save the model choice: %s", exc)
        return jsonify(error=f"could not save the model choice: {exc}"), 500
    body = _system_body()
    body["applied_model"] = applied
    return jsonify(body)
