"""Ask Groq for gardening advice about the current machine state.

POST a JSON body of ``{"question": "..."}`` to get back the model's answer plus
the token usage for the call.

This route is not wrapped in ``check_sensor_guard``: that guard models a single
hardware sensor being absent, whereas the failure modes here are "not
configured" and "upstream call failed". It follows the camera routes instead,
which map their own conditions onto 4xx/5xx explicitly.

The endpoint is covered by the existing ``_register_auth`` hook like every
other route except ``/``, ``/health``, and ``/static``, so with
``GARDEN_ADMIN_PASSWORD`` set it already requires ``X-API-Key`` from non-localhost
callers.
"""

import logging

from flask import Blueprint, jsonify, request

from app.integrations import groq

logger = logging.getLogger(__name__)

advice_blueprint = Blueprint("advice", __name__)


@advice_blueprint.route("", methods=["POST"])
@advice_blueprint.route("/ask", methods=["POST"])
def ask():
    """Return the model's advice for the current garden state."""
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    if not question:
        return jsonify(error="a non-empty 'question' is required"), 400

    include_image = bool(payload.get("include_image", True))

    # The web UI keeps the Groq key in localStorage and sends it per request,
    # mirroring how it supplies the admin password, so the Pi never has to
    # store it. Falls back to the server-side GROQ_API_KEY when absent.
    api_key = request.headers.get("X-Groq-Key", "")

    if not groq.is_enabled(api_key):
        return (
            jsonify(
                error="no Groq API key: add one in the web UI settings, or set "
                "GROQ_API_KEY in the Pi's .env"
            ),
            503,
        )

    try:
        result = groq.advise(question, api_key=api_key, include_image=include_image)
    except groq.AdviceError as exc:
        return jsonify(error=str(exc)), 502

    return jsonify(result), 200
