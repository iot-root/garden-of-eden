import logging

from flask import Blueprint, jsonify, request

import config
from app.lib import state as state_lib
from app.lib.hardware import get_pin_factory
from app.lib.lib import check_sensor_guard, parse_level

from .light import Light as LightControl

logger = logging.getLogger(__name__)

light_blueprint = Blueprint("light", __name__)

try:
    light_control = LightControl(
        pin=config.LIGHT_PIN,
        frequency=config.LIGHT_FREQUENCY,
        pin_factory=get_pin_factory(),
    )
except Exception as exc:
    logger.error("Failed to initialize Light: %s", exc)
    light_control = None

check_sensor = check_sensor_guard(sensor=light_control, sensor_name="Light")


@light_blueprint.route("/on", methods=["POST"])
@check_sensor
def turn_on():
    light_control.on()
    state_lib.save_state(light_on=True)
    return jsonify(message="Light turned on!"), 200


@light_blueprint.route("/off", methods=["POST"])
@check_sensor
def turn_off():
    light_control.off()
    state_lib.save_state(light_on=False)
    return jsonify(message="Light turned off!"), 200


@light_blueprint.route("/brightness", methods=["POST"])
@check_sensor
def set_brightness():
    data = request.get_json(silent=True) or {}
    brightness_value = parse_level(data, default=config.DEFAULT_BRIGHTNESS)
    light_control.set_brightness(brightness_value)
    state_lib.save_state(light_on=brightness_value > 0, brightness=brightness_value)
    return jsonify(message=f"Light adjusted to {brightness_value}%"), 200


@light_blueprint.route("/brightness", methods=["GET"])
@check_sensor
def get_brightness():
    brightness_value = light_control.get_brightness()
    return jsonify(value=brightness_value), 200
