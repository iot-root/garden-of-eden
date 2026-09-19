import logging
import threading

from flask import Blueprint, jsonify, request

import config
from app.lib import state as state_lib
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

# Tracks the pending auto-off timer so repeated calls don't stack and so the
# pump is *always* armed with a shut-off. Whenever the pump is energized
# (on/run/speed>0) we (re)arm a timer for at most MAX_PUMP_RUN_SECONDS;
# turning it off cancels it.
_run_timer = None
_run_lock = threading.Lock()


def _safety_off():
    """Stop the pump and record it off, so persisted state stays accurate."""
    pump_control.off()
    state_lib.save_state(pump_on=False)


def _arm_auto_off(seconds):
    """(Re)arm the single auto-off timer to stop the pump after ``seconds``."""
    global _run_timer
    with _run_lock:
        if _run_timer is not None:
            _run_timer.cancel()  # supersede any in-flight run
        _run_timer = threading.Timer(seconds, _safety_off)
        _run_timer.daemon = True
        _run_timer.start()


def _cancel_auto_off():
    global _run_timer
    with _run_lock:
        if _run_timer is not None:
            _run_timer.cancel()
            _run_timer = None


@pump_blueprint.route("/on", methods=["POST"])
@check_sensor
def turn_on():
    pump_control.on()
    # Never leave the pump running longer than the cap, even if nobody calls /off.
    _arm_auto_off(config.MAX_PUMP_RUN_SECONDS)
    state_lib.save_state(pump_on=True)
    return jsonify(message="Pump turned on!"), 200


@pump_blueprint.route("/off", methods=["POST"])
@check_sensor
def turn_off():
    pump_control.off()
    _cancel_auto_off()
    state_lib.save_state(pump_on=False)
    return jsonify(message="Pump turned off!"), 200


@pump_blueprint.route("/speed", methods=["POST"])
@check_sensor
def adjust_speed():
    data = request.get_json(silent=True) or {}
    speed_value = parse_level(data, default=config.DEFAULT_PUMP_SPEED)
    pump_control.set_speed(speed_value)
    # A non-zero speed energizes the pump, so arm the shut-off too.
    if speed_value > 0:
        _arm_auto_off(config.MAX_PUMP_RUN_SECONDS)
    else:
        _cancel_auto_off()
    state_lib.save_state(pump_on=speed_value > 0, speed=speed_value)
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
        seconds = int(data.get("seconds", config.MAX_PUMP_RUN_SECONDS))
    except (TypeError, ValueError):
        return jsonify(message="seconds must be an integer"), 400
    if not (1 <= seconds <= config.MAX_PUMP_RUN_SECONDS):
        return (
            jsonify(message=f"seconds must be between 1 and {config.MAX_PUMP_RUN_SECONDS}"),
            400,
        )

    pump_control.on()
    _arm_auto_off(seconds)
    state_lib.save_state(pump_on=True)
    return jsonify(message=f"Pump running for {seconds}s"), 200


@pump_blueprint.route("/stats", methods=["GET"])
@check_sensor
def get_pump_data():
    data = fetch_ina219_data()
    return jsonify(data)
