import logging

from flask import Blueprint, jsonify

from app.lib.hardware import get_pin_factory
from app.lib.lib import check_sensor_guard

from .distance import Distance as DistanceControl

logger = logging.getLogger(__name__)

distance_blueprint = Blueprint("distance", __name__)

try:
    distance_control = DistanceControl(pin_factory=get_pin_factory())
except Exception as exc:
    logger.error("Failed to initialize Distance: %s", exc)
    distance_control = None

check_sensor = check_sensor_guard(sensor=distance_control, sensor_name="Distance")


@distance_blueprint.route("", methods=["GET"])
@distance_blueprint.route("/measure", methods=["GET"])
@check_sensor
def get_distance():
    distance_value = distance_control.measure_once()
    return jsonify(distance=distance_value), 200
