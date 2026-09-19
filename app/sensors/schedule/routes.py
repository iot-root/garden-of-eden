import logging

from flask import Blueprint, jsonify, request

from . import schedule as sched

logger = logging.getLogger(__name__)

schedule_blueprint = Blueprint("schedule", __name__)


@schedule_blueprint.route("", methods=["GET"])
def get_schedule():
    return jsonify(sched.load_schedule())


@schedule_blueprint.route("", methods=["POST"])
def set_schedule():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="expected a JSON schedule object"), 400
    try:
        applied = sched.apply_schedule(data)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    except FileNotFoundError:
        # crontab binary missing (e.g. off-Pi) — schedule is still saved.
        return jsonify(error="crontab not available on this host"), 503
    return jsonify(applied)
