from flask import Blueprint, jsonify

import config
from app.lib.hardware import detect_model

system_blueprint = Blueprint("system", __name__)


def _profile_for(model):
    """Resolve a hardware profile for a model string. Falls back to a prefix
    match so custom/suffixed names (e.g. 'gardyn 3.0 (simulated)') still map to
    the closest known profile instead of returning empty."""
    if model in config.MODELS:
        return config.MODELS[model]
    for key, profile in config.MODELS.items():
        if model and (model.startswith(key) or key in model):
            return profile
    return {}


@system_blueprint.route("", methods=["GET"])
def get_system():
    """Report identity, version, and the detected hardware model/profile."""
    model = detect_model()
    return jsonify(
        {
            "identifier": config.IDENTIFIER,
            "version": config.VERSION,
            "model": model,
            "profile": _profile_for(model),
            "sensor_type": config.SENSOR_TYPE,
            "water_low_cm": config.WATER_LOW_CM,
            "pump_max_run_seconds": config.MAX_PUMP_RUN_SECONDS,
        }
    )
