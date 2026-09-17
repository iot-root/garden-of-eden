import logging
import threading

from flask import Blueprint, jsonify, request

import config
from app.lib.hardware import get_pin_factory
from app.lib.lib import check_sensor_guard, parse_level

from .pump import Pump as PumpControl
from .pump_power import fetch_ina219_data

logger = logging.getLogger(__name__)

pump_blueprint = Blueprint("pump", __name__)

try:
    pump_control = PumpControl(
        pin=config.PUMP_PIN,
        frequency=config.PUMP_FREQUENCY,
        pin_factory=get_pin_factory(),
    )
except Exception as exc:
    logger.error("Failed to initialize Pump: %s", exc)
    pump_control = None

check_sensor = check_sensor_guard(sensor=pump_control, sensor_name="Pump")

# Tracks the pending auto-off timer for /pump/run so repeated calls don't stack.
_run_timer = None
_run_lock = threading.Lock()


@pump_blueprint.route("/on", methods=["POST"])
@check_sensor
def turn_on():
    pump_control.on()
    return jsonify(message="Pump turned on!"), 200


@pump_blueprint.route("/off", methods=["POST"])
@check_sensor
def turn_off():
    pump_control.off()
    return jsonify(message="Pump turned off!"), 200


@pump_blueprint.route("/speed", methods=["POST"])
@check_sensor
def adjust_speed():
    data = request.get_json(silent=True) or {}
    speed_value = parse_level(data, default=config.DEFAULT_PUMP_SPEED)
    pump_control.set_speed(speed_value)
    return jsonify(message=f"Pump adjusted to {speed_value}% speed!"), 200


@pump_blueprint.route("/speed", methods=["GET"])
@check_sensor
def get_speed():
    current_speed = pump_control.get_speed()
    return jsonify(value=current_speed), 200


@pump_blueprint.route("/run", methods=["POST"])
@check_sensor
def run_for():
    """Run the pump for a fixed number of seconds, then stop. Non-blocking:
    schedules the stop on a background timer and returns immediately."""
    data = request.get_json(silent=True) or {}
    try:
        seconds = int(data.get("seconds", 300))
    except (TypeError, ValueError):
        return jsonify(message="seconds must be an integer"), 400
    if not (1 <= seconds <= 3600):
        return jsonify(message="seconds must be between 1 and 3600"), 400

    global _run_timer
    with _run_lock:
        if _run_timer is not None:
            _run_timer.cancel()  # supersede any in-flight run
        pump_control.on()
        _run_timer = threading.Timer(seconds, pump_control.off)
        _run_timer.daemon = True
        _run_timer.start()
    return jsonify(message=f"Pump running for {seconds}s"), 200


@pump_blueprint.route("/stats", methods=["GET"])
@check_sensor
def get_pump_data():
    data = fetch_ina219_data()
    return jsonify(data)
