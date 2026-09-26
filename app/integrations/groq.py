"""Groq gardening advice.

Sends a snapshot of the current garden state -- sensor readings, actuator
state, grow-cycle progress -- plus the most recent upper-camera frame to the
Groq chat completions API and returns practical instructions for the operator.

This replaced the earlier Anthropic/Claude integration. Groq is used because it
offers a genuine free tier (no credit card, 30 requests/minute and 1000
requests/day on the free plan), whereas the Anthropic API is prepaid-credit
only and rejects calls once the balance is exhausted.

Three deliberate constraints:

- The ``groq`` SDK is imported lazily inside ``_client()`` so the module
  imports cleanly on a host that has not installed the dependency yet, which
  keeps the test suite and the rest of the app runnable without it.
- ``GROQ_API_KEY`` is an *outbound* credential. It is unrelated to
  ``GARDEN_ADMIN_PASSWORD``, which authenticates inbound REST callers. Nothing
  here logs the key.
- The Groq API is OpenAI-compatible, so requests go to
  ``/openai/v1/chat/completions`` with the system prompt as a ``system``
  message rather than a separate ``system=`` argument.

Only the most recent upper-camera frame is sent. The timelapse archive
(``camera.archive_frame``) would be the natural source for historical frames,
but it is populated solely by the MQTT publisher, which is not installed as a
service, so no history exists to draw on yet.
"""

import base64
import json
import logging
import os
from datetime import datetime

import config
from app.lib import grow as grow_lib
from app.lib import state as state_lib
from app.lib.hardware import detect_model, lower_camera_enabled, profile_for
from app.lib.water import gallons_remaining, is_water_low

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a knowledgeable indoor-gardening assistant for a Gardyn "
    "hydroponic garden controller. You are given a JSON snapshot of the "
    "current machine state and, when available, a photo from the upper "
    "camera.\n\n"
    "Answer with specific, actionable steps the operator can take on the "
    "machine: light level and duration, pump schedule and speed, water top-ups, "
    "nutrient timing, and what (if anything) needs attention right now. "
    "Reference the actual readings you were given rather than generic advice, "
    "and say plainly when a reading is missing or looks wrong. Keep it short "
    "and concrete. Do not invent sensor values that were not supplied."
)


class AdviceError(Exception):
    """Raised when a Groq call cannot be completed."""


def is_enabled(api_key=None):
    """True when a Groq key is available.

    ``api_key`` is the optional per-request key supplied by the browser (the
    web UI keeps it in localStorage and sends it as X-Groq-Key, the same way
    it supplies the admin password). Falling back to the server-side
    ``GROQ_API_KEY`` keeps the endpoint usable from scripts/curl.
    """
    return bool((api_key or "").strip() or config.GROQ_API_KEY)


def _client(api_key=None):
    """Build a Groq client, importing the SDK lazily.

    Prefers the caller-supplied key over the server-side one.
    """
    try:
        from groq import Groq
    except ImportError as exc:  # pragma: no cover - depends on host install
        raise AdviceError("the 'groq' package is not installed on this host") from exc
    return Groq(
        api_key=(api_key or "").strip() or config.GROQ_API_KEY,
        timeout=config.GROQ_TIMEOUT,
    )


def _read(label, read_fn):
    """Read one value, returning ``None`` instead of raising.

    A single unavailable sensor must not stop us answering the rest of the
    question, so every probe is isolated and reported as null.
    """
    try:
        return read_fn()
    except Exception as exc:  # noqa: BLE001 - a bad sensor is not fatal here
        logger.warning("Advice snapshot: %s unavailable (%s)", label, exc)
        return None


def _days_since(started_iso):
    """Whole days since an ISO timestamp, or None if unparseable."""
    try:
        return (datetime.now() - datetime.fromisoformat(started_iso)).days
    except (TypeError, ValueError):
        return None


def snapshot():
    """Build a JSON-friendly snapshot of the current garden state.

    Every field is best-effort: a sensor that fails to read shows up as
    ``None`` so the model can say so instead of the request failing outright.
    """
    from app.sensors.distance.routes import distance_control
    from app.sensors.humidity.humidity import humidity_sensor
    from app.sensors.pcb_temp.pcb_temp import get_pcb_temperature
    from app.sensors.temperature.temperature import temperature_sensor

    model = _read("model", detect_model)

    distance_cm = None
    if distance_control is not None:
        distance_cm = _read("water level", distance_control.measure_once)

    grow = _read("grow state", grow_lib.load_state) or {}
    lower_camera = _read("lower camera", lower_camera_enabled)

    return {
        "model": model,
        "profile": _read("profile", lambda: dict(profile_for(model))) if model else None,
        "cameras": None if lower_camera is None else (2 if lower_camera else 1),
        "air_temperature_c": _read("air temperature", temperature_sensor.read),
        "humidity_percent": _read("humidity", humidity_sensor.read),
        "pcb_temperature_c": _read("pcb temperature", get_pcb_temperature),
        "water_distance_cm": distance_cm,
        "water_gallons_remaining": (
            gallons_remaining(
                distance_cm,
                config.WATER_FULL_CM,
                config.WATER_EMPTY_CM,
                config.TANK_CAPACITY_GALLONS,
            )
            if distance_cm is not None
            else None
        ),
        "water_low": is_water_low(distance_cm, config.WATER_LOW_CM),
        "actuators": _read("actuator state", state_lib.load_state),
        "grow": {
            "stage": grow.get("stage"),
            "days_elapsed": _days_since(grow.get("started")),
            "reminders_due": _read("reminders", lambda: sorted(grow_lib.due_reminders(grow))),
        },
    }


def _image_block(path):
    """Return a base64 image content part, or None if unavailable.

    Groq takes OpenAI-style ``image_url`` parts, where a data URI carries the
    base64 payload inline. The upstream JPEG is typically well under the 20MB
    per-request image limit.
    """
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as fh:
            data = base64.standard_b64encode(fh.read()).decode("ascii")
    except OSError as exc:
        logger.warning("Advice snapshot: could not read %s (%s)", path, exc)
        return None
    return {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{data}"}}


def build_content(question, include_image=True):
    """Assemble the user message: image part first, then the text context.

    Images are placed before text, since the model then reads them while the
    question is freshest.
    """
    content = []
    if include_image:
        block = _image_block(config.UPPER_IMAGE_PATH)
        if block:
            content.append(block)
        else:
            logger.info("Advice request: no camera frame at %s", config.UPPER_IMAGE_PATH)

    state = snapshot()
    content.append(
        {
            "type": "text",
            "text": (
                "Current machine state:\n```json\n"
                f"{json.dumps(state, indent=2, default=str)}\n```\n\n"
                f"Question: {question}"
            ),
        }
    )
    return content


def _error_detail(exc):
    """Extract a safe, human-readable reason from an SDK/API error.

    Prefers the API's own ``error.type`` / ``error.message`` from the response
    body, which is what actually explains a failure (unknown model id, image
    over the size limit, rate limit, revoked key). Falls back to the exception
    class name. Deliberately never uses ``repr(exc)`` or the full body: SDK
    errors can embed request headers, and the request carries the caller's API
    key.
    """
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        err = body.get("error", body)
        if isinstance(err, dict):
            msg = err.get("message")
            kind = err.get("type")
            if msg and kind:
                return f"{kind}: {msg}"
            if msg:
                return str(msg)
            if kind:
                return str(kind)
    status = getattr(exc, "status_code", None)
    if status:
        return f"HTTP {status}"
    return type(exc).__name__


def _response_text(response):
    """Pull the answer text out of a chat completion.

    The configured model can run in a reasoning mode, where the visible answer
    arrives in ``content`` and the chain of thought in ``reasoning``. If
    ``content`` comes back empty we fall back to ``reasoning`` rather than
    reporting an empty response, since a truncated or fully-reasoned turn still
    tells the operator something.
    """
    choices = getattr(response, "choices", None) or []
    if not choices:
        return ""
    message = getattr(choices[0], "message", None)
    if message is None:
        return ""
    text = (getattr(message, "content", None) or "").strip()
    if text:
        return text
    return (getattr(message, "reasoning", None) or "").strip()


def advise(question, api_key=None, include_image=True):
    """Ask the model for advice about the current state.

    ``api_key`` is the optional per-request key from the browser; when absent
    the server-side ``GROQ_API_KEY`` is used instead.

    Returns ``{"advice", "model", "usage"}``. Raises ``AdviceError`` if no key
    is available or the API call fails.
    """
    if not is_enabled(api_key):
        raise AdviceError("no Groq API key available")

    try:
        response = _client(api_key).chat.completions.create(
            model=config.GROQ_MODEL,
            max_completion_tokens=config.GROQ_MAX_TOKENS,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_content(question, include_image)},
            ],
        )
    except AdviceError:
        raise
    except Exception as exc:  # noqa: BLE001 - SDK/network errors vary widely
        detail = _error_detail(exc)
        # Never log the exception repr: SDK errors can embed request headers
        # (and therefore the key). The API's own error type/message is safe and
        # is the only thing that makes a failure diagnosable.
        logger.error("Groq advice call failed: %s (%s)", type(exc).__name__, detail)
        raise AdviceError(f"Groq request failed: {detail}") from exc

    text = _response_text(response)
    if not text:
        raise AdviceError("Groq returned an empty response")

    usage_obj = getattr(response, "usage", None)
    usage = {
        "input_tokens": getattr(usage_obj, "prompt_tokens", None),
        "output_tokens": getattr(usage_obj, "completion_tokens", None),
    }
    logger.info(
        "Groq advice from %s (in=%s out=%s tokens)",
        config.GROQ_MODEL,
        usage["input_tokens"],
        usage["output_tokens"],
    )
    return {"advice": text, "model": config.GROQ_MODEL, "usage": usage}
