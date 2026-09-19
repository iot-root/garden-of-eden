"""ThingsBoard telemetry forwarding (issue #24) — scaffold.

When THINGSBOARD_ENABLED is set, sensor telemetry can be forwarded to a
ThingsBoard instance. ThingsBoard accepts telemetry over MQTT on topic
``v1/devices/me/telemetry`` (auth via a device access token) or over HTTP at
``/api/v1/<token>/telemetry``.

This module is a documented stub: it validates config and logs intent. Wire the
actual publish call where telemetry is gathered (e.g. mqtt.py publish_* threads)
once you have a device token. See docs/integrations/thingsboard.md.
"""

import json
import logging

import config

logger = logging.getLogger(__name__)


def is_enabled():
    return bool(config.THINGSBOARD_ENABLED and config.THINGSBOARD_HOST and config.THINGSBOARD_TOKEN)


def publish_telemetry(data):
    """Forward a dict of telemetry to ThingsBoard. No-op unless configured.

    Returns True if it attempted a send, False if disabled.
    """
    if not is_enabled():
        return False

    # TODO: implement the actual transport. Example (HTTP) once `requests` is
    # available on the device:
    #   url = f"https://{config.THINGSBOARD_HOST}/api/v1/{config.THINGSBOARD_TOKEN}/telemetry"
    #   requests.post(url, json=data, timeout=5)
    logger.info("ThingsBoard telemetry (stub): %s", json.dumps(data))
    return True
