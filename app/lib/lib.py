import logging
from functools import wraps

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def parse_level(data, key="value", default=None):
    """Pull a 0..100 numeric level from a request body, raising ValueError
    (-> HTTP 400 via the guard) on missing/non-numeric/out-of-range input."""
    value = (data or {}).get(key, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"'{key}' must be a number between 0 and 100")
    if not (0 <= value <= 100):
        raise ValueError(f"'{key}' must be between 0 and 100")
    return value


def check_sensor_guard(sensor, sensor_name):
    """Decorator that guards a route against missing/failing hardware.

    - If the sensor failed to initialize (``None``) -> HTTP 400.
    - If the handler raises while talking to hardware (disconnected sensor,
      I2C/GPIO error) -> HTTP 503 instead of a 500, so clients can tell the
      difference between "broken request" and "hardware unavailable" (#57).
    """

    def decorator(func):
        # @wraps preserves the wrapped function's metadata, otherwise Flask
        # complains about duplicate endpoint names.
        @wraps(func)
        def check_sensor(*args, **kwargs):
            if sensor is None:
                return jsonify(error=f"{sensor_name} is not initialized"), 400
            try:
                return func(*args, **kwargs)
            except ValueError as exc:
                # Validation errors are the caller's fault -> 400.
                return jsonify(error=str(exc)), 400
            except HTTPException:
                # Let Flask's own errors (400 bad JSON, 415, 404…) pass through.
                raise
            except Exception as exc:
                logger.error("%s hardware error: %s", sensor_name, exc)
                return (
                    jsonify(error=f"{sensor_name} hardware unavailable: {exc}"),
                    503,
                )

        return check_sensor

    return decorator
