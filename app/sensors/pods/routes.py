import logging

from flask import Blueprint, jsonify, request

import config
from app.lib import pods as pods_lib

logger = logging.getLogger(__name__)

pods_blueprint = Blueprint("pods", __name__)


@pods_blueprint.route("", methods=["GET"])
def get_pods():
    from app.lib import hardware

    return jsonify(
        {
            "pods": pods_lib.with_positions(pods_lib.load_pods()),
            "shapes": pods_lib.SHAPES,
            "catalog": pods_lib.load_catalog(),
            "layout": {
                "columns": hardware.tower_count(),
                "pods": hardware.pod_capacity(),
                "side_pattern": config.POD_SIDE_PATTERN or "",
            },
        }
    )


@pods_blueprint.route("", methods=["POST"])
def set_pods():
    data = request.get_json(silent=True)
    if not isinstance(data, list):
        return jsonify(error="expected a JSON list of pods"), 400
    return jsonify(pods_lib.with_positions(pods_lib.save_pods(data)))


@pods_blueprint.route("/<int:pod_id>", methods=["POST"])
def set_one(pod_id):
    data = request.get_json(silent=True) or {}
    saved = pods_lib.set_pod(pod_id, name=data.get("name"), symbols=data.get("symbols"))
    return jsonify(pods_lib.with_positions(saved))
