"""Operator-chosen hardware model, persisted separately from the environment.

The model normally comes from ``GARDYN_MODEL`` in ``.env``, falling back to
inference from the temperature/humidity chip. That suits a fixed installation but
is awkward to change: it needs an edit to a credentials-bearing file plus a
service restart. This module lets the web UI pick the model instead.

Two decisions worth stating:

- It is stored in its own small JSON file rather than written back into ``.env``.
  ``.env`` holds the admin password and the Groq key, and ``bin/setup.sh``
  owns it; rewriting it from a web request risks corrupting the service config.
- It is read on every call, never cached at import. That is what lets a change
  take effect immediately instead of needing a restart.

Precedence, highest first:

1. the model chosen here (most deliberate, most recent),
2. ``GARDYN_MODEL`` from the environment,
3. inference from the sensor chip,
4. the model default.

:func:`describe_source` reports which of these supplied the active model so the
UI can say so, rather than leaving a stale-looking ``.env`` value to confuse.
"""

import json
import logging

import config
from app.lib.persist import write_json_atomic

logger = logging.getLogger(__name__)

AUTO = "auto"


def available_models():
    """Known model names, plus the automatic option, for the UI dropdown."""
    from app.lib import models

    return [AUTO] + sorted(models.MODELS)


def _read():
    try:
        with open(config.HARDWARE_FILE) as fh:
            data = json.load(fh)
    except (FileNotFoundError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def get_model_override():
    """The model chosen in the UI, or None when set to automatic."""
    value = str(_read().get("model") or "").strip()
    if not value or value == AUTO:
        return None
    return value


def set_model_override(model):
    """Persist a model choice. ``None`` or ``"auto"`` clears it.

    Raises ``ValueError`` for an unknown name, so a typo can never leave the
    unit pointed at a model that does not exist.
    """
    from app.lib import models

    name = str(model or "").strip()
    if not name or name == AUTO:
        write_json_atomic(config.HARDWARE_FILE, {"model": AUTO})
        return None
    resolved = models.model_for(name)
    if resolved.name.lower() != name.lower():
        raise ValueError(f"unknown model: {name}")
    write_json_atomic(config.HARDWARE_FILE, {"model": resolved.name})
    return resolved.name


def describe_source():
    """Where the active model came from: "settings", "environment" or "auto"."""
    if get_model_override():
        return "settings"
    if config.MODEL_OVERRIDE:
        return "environment"
    return "auto"
