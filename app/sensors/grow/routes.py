from flask import Blueprint, jsonify, request

from app.lib import grow as grow_lib

grow_blueprint = Blueprint("grow", __name__)


@grow_blueprint.route("", methods=["GET"])
def get_grow():
    state = grow_lib.load_state()
    return jsonify({**state, "due": grow_lib.due_reminders(state)})


@grow_blueprint.route("/start", methods=["POST"])
def start_grow():
    return jsonify(grow_lib.start_cycle())


@grow_blueprint.route("/stage", methods=["POST"])
def set_stage():
    data = request.get_json(silent=True) or {}
    try:
        state = grow_lib.set_stage(grow_lib.load_state(), data.get("stage"))
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    grow_lib.save_state(state)
    return jsonify(state)


@grow_blueprint.route("/acknowledge", methods=["POST"])
def acknowledge():
    data = request.get_json(silent=True) or {}
    key = data.get("key")
    if not key:
        return jsonify(error="missing 'key'"), 400
    state = grow_lib.acknowledge(grow_lib.load_state(), key)
    grow_lib.save_state(state)
    return jsonify(state)
