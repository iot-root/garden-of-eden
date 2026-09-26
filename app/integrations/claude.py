"""Claude (Anthropic) gardening advice.

Sends a snapshot of the current garden state -- sensor readings, actuator
state, grow-cycle progress -- plus the most recent upper-camera frame to the
Claude Messages API and returns practical instructions for the operator.

Unlike alexa.py and thingsboard.py, which are transport scaffolds, this is a
working integration (issue #101). Two deliberate constraints:

- The ``anthropic`` SDK is imported lazily inside ``_client()`` so the module
  imports cleanly on a host that has not installed the dependency yet, which
  keeps the test suite and the rest of the app runnable without it.
- ``ANTHROPIC_API_KEY`` is an *outbound* credential. It is unrelated to
  ``GARDEN_ADMIN_PASSWORD``, which authenticates inbound REST callers. Nothing here
  logs the key.

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
    """Raised when a Claude call cannot be completed."""


def is_enabled(api_key=None):
    """True when a Claude key is available.

    ``api_key`` is the optional per-request key supplied by the browser (the
    web UI keeps it in localStorage and sends it as X-Claude-Key, the same way
    it supplies the admin password). Falling back to the server-side
    ``ANTHROPIC_API_KEY`` keeps the endpoint usable from scripts/curl.
    """
    return bool((api_key or "").strip() or config.ANTHROPIC_API_KEY)


def _client(api_key=None):
    """Build an Anthropic client, importing the SDK lazily.

    Prefers the caller-supplied key over the server-side one.
    """
    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover - depends on host install
        raise AdviceError("the 'anthropic' package is not installed on this host") from exc
    return anthropic.Anthropic(
        api_key=(api_key or "").strip() or config.ANTHROPIC_API_KEY,
        timeout=config.ANTHROPIC_TIMEOUT,
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
    """Return a base64 image content block, or None if unavailable."""
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as fh:
            data = base64.standard_b64encode(fh.read()).decode("ascii")
    except OSError as exc:
        logger.warning("Advice snapshot: could not read %s (%s)", path, exc)
        return None
    return {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": data}}


def build_content(question, include_image=True):
    """Assemble the user message: image block first, then the text context.

    Anthropic's guidance is to place images before text, since the model then
    reads them while the question is freshest.
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


def advise(question, api_key=None, include_image=True):
    """Ask Claude for advice about the current state.

    ``api_key`` is the optional per-request key from the browser; when absent
    the server-side ``ANTHROPIC_API_KEY`` is used instead.

    Returns ``{"advice", "model", "usage"}``. Raises ``AdviceError`` if no key
    is available or the API call fails.
    """
    if not is_enabled(api_key):
        raise AdviceError("no Claude API key available")

    try:
        response = _client(api_key).messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=config.ANTHROPIC_MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_content(question, include_image)}],
        )
    except AdviceError:
        raise
    except Exception as exc:  # noqa: BLE001 - SDK/network errors vary widely
        # Never echo the exception repr: SDK errors can embed request headers
        # (and therefore the key). Log the type, return a generic message.
        logger.error("Claude advice call failed: %s", type(exc).__name__)
        raise AdviceError(f"Claude request failed ({type(exc).__name__})") from exc

    text = "".join(block.text for block in response.content if block.type == "text")
    usage = {
        "input_tokens": getattr(response.usage, "input_tokens", None),
        "output_tokens": getattr(response.usage, "output_tokens", None),
    }
    logger.info(
        "Claude advice from %s (in=%s out=%s tokens)",
        config.ANTHROPIC_MODEL,
        usage["input_tokens"],
        usage["output_tokens"],
    )
    return {"advice": text, "model": config.ANTHROPIC_MODEL, "usage": usage}
